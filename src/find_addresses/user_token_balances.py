import requests
import json
import asyncio
import aiohttp
from sanic import Blueprint
from utils.utils import Response
from utils.errors import CustomError
from utils.authorization import is_subscribed
import os
from loguru import logger
from google.cloud import bigquery
from sanic.request import RequestParameters
import requests
from caching.cache_utils import cache_validity, get_cache, set_cache, delete_cache
from data.populate_db import check_coingecko_tokens_staleness
from data.populate_blockdaemon import populate_erc1155_blockdaemon,\
         populate_erc721_blockdaemon, check_blockDaemon_tokens_staleness


import re
from caching.cache_utils import cache_validity, get_cache, set_cache, delete_cache

USER_TOKEN_BALANCE_BP = Blueprint("userbalance", url_prefix='/userbalance', version=1)

def make_query_string(request_args: dict, args_list: list) -> str:
    query_string = ""
    for (key, value) in request_args.items():
        if key in args_list:
            if type(value) == list:
                value = value[0]
            query_string += f"&{key}={value}"
    return query_string[1:] # to remove the first $ sign appened to the string

@USER_TOKEN_BALANCE_BP.post('populate_tokens')
@is_subscribed()
async def populate_tokens(request):

    await asyncio.gather(*[populate_erc721_blockdaemon(request.app),
        populate_erc1155_blockdaemon(request.app)
        ])
    return Response.success_response(data={})




@USER_TOKEN_BALANCE_BP.get('token_balances')
@is_subscribed()
async def token_balances(request):
    wallet_address = request.args.get('wallet_address')
    await fetch_nft_balance(request.app, request.args, "ethereum")
  
    # if not wallet_address:
    #     raise CustomError("Wallet address is required")
    
    # query_string: str = make_query_string(request.args, ["chain", "wallet_address"])

    # if request.app.config.CACHING:
    #     caching_key = f"{request.route.path}?{query_string}"
    #     logger.info(f"Here is the caching key {caching_key}")
    #     data = await wallet_balance_caching(request.app, caching_key, request.args)
    # else:
    #     data = await wallet_balance_caching(request.app, request.args)
       
    return Response.success_response(data=data)


async def wallet_balance_caching(app: object, caching_key: str, request_args: dict) -> any: 
    cache_valid = await cache_validity(app.config.REDIS_CLIENT, caching_key, 
                            app.config.CACHING_TTL['LEVEL_ONE'])

    if not cache_valid:
        data = await fetch_wallet_balance(app, request_args)
        if data: #only set cache when data is not empty
            await set_cache(app.config.REDIS_CLIENT, caching_key, data)
        return data
    result= await get_cache(app.config.REDIS_CLIENT, caching_key)
    return json.loads(result)


async def fetch_wallet_balance(app: object, request_args: RequestParameters) -> list:
    await check_coingecko_tokens_staleness(app)
    await check_blockDaemon_tokens_staleness(app) ##this checks if the coingecko token list in db is not older than 5 hours
    headers = {'Content-type': 'application/json'}
    params = {"jsonrpc":"2.0","method":"alchemy_getTokenBalances",
            "params": [request_args.get('wallet_address').lower(), "erc20"],"id":"42"}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(app.config.WEB3_PROVIDER, json=params, headers=headers) as resp:
            response  = await resp.json()
    result = []
    logger.info(response)
    for e in response["result"]["tokenBalances"]:
        contract_address = e["contractAddress"]
        token_balance = e["tokenBalance"]
        _contract_address =  await app.config.TOKENS.find_one({"ethereum": contract_address.lower()}, 
                        projection={"ethereum":  True, "name": True})
        if _contract_address:
            contract_address = _contract_address.get("name")
            token_balance = token_balance.replace("0x", "")
            if token_balance:
                try:
                    balance = int(token_balance, 16)/10**18
                    if not round(balance, 2) <= 0.0:
                        result.append({"contract_address": contract_address, "balance": round(balance, 3)})
                except Exception:
                    continue
    return result


"""
Get assets related to a wallet address from Block Daemon
"""
async def fetch_nft_balance(app: object, request_args: RequestParameters, chain: str) -> list:
    logger.info ("\n\n")
    logger.info(os.environ['BLOCK_DAEMON_SECRET'])
    logger.info ("\n\n")
    params = {"wallet_address": request_args.get('wallet_address').lower()}
    logger.info (params)
    headers = {'X-API-Key': os.environ["BLOCK_DAEMON_SECRET"] }
    logger.info (headers)
    # headers = {'Content-type': 'application/json', "Authorization": f"Bearer {os.environ['BLOCK_DAEMON_SECRET']}"}

    async with aiohttp.ClientSession() as session:
        async with session.get("https://svc.blockdaemon.com/nft/v1/ethereum/mainnet/assets", params=params, headers=headers) as resp:
            response  = await resp.json()


    if not response:
        return []
    return response["data"]