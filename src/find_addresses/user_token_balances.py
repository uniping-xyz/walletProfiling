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
from data.populate_coingecko import check_coingecko_tokens_staleness
from data.populate_blockdaemon import populate_erc1155_blockdaemon,\
         populate_erc721_blockdaemon, check_blockDaemon_tokens_staleness

from find_addresses.db_calls.erc20.ethereum import search_contract_address as erc20_eth_search
from find_addresses.db_calls.erc721.ethereum import search_contract_address as erc721_eth_search
from find_addresses.db_calls.erc1155.ethereum import search_contract_address as erc1155_eth_search



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


@USER_TOKEN_BALANCE_BP.get('token_balances')
@is_subscribed()
async def token_balances(request):
    wallet_address = request.args.get('wallet_address')
    chain = request.args.get('chain')

    # await fetch_nft_balance(request.app, request.args, "ethereum")
  
    if not wallet_address:
        raise CustomError("Wallet address is required")
    
    if not chain:
        raise CustomError("chain is required")

    query_string: str = make_query_string(request.args, ["chain", "wallet_address"])

    caching_key = f"{request.route.path}?{query_string}"
    logger.info(f"Here is the caching key {caching_key}")
    data = await wallet_balance_caching(request.app, caching_key, request.args)
       
    return Response.success_response(data=data)


async def wallet_balance_caching(app: object, caching_key: str, request_args: dict) -> any: 
    cache_valid = await cache_validity(app.config.REDIS_CLIENT, caching_key, 
                            app.config.CACHING_TTL['LEVEL_FOUR'])

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
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
     }
    
    params = {"jsonrpc": "2.0",
            "method":"alchemy_getTokenBalances", 
            "params": [request_args.get("wallet_address")],"id":"1"}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(app.config.WEB3_PROVIDER, json=params, headers=headers) as resp:
            response  = await resp.json()
    logger.info(app.config.WEB3_PROVIDER)
    result = []
    logger.info(response)


    result = []

    for e in response["result"]["tokenBalances"]:
        contract_address = e["contractAddress"]
        token_balance = e["tokenBalance"]
        contract_name =  await search_erc20_contract_address(app, request_args.get("chain"), contract_address)
        logger.info(contract_name)
        if contract_name:
            token_balance = token_balance.replace("0x", "")
            if token_balance:
                try:
                    balance = int(token_balance, 16)/10**18
                    if not round(balance, 2) <= 0.0:
                        result.append({"contract_address": contract_address, "contract_name": contract_name, "balance": round(balance, 3)})
                except Exception:
                    continue
    return result



"""
Get assets related to a wallet address from Block Daemon
"""
async def fetch_nft_balance(app, request_args) -> list:
    logger.info(os.environ['BLOCK_DAEMON_SECRET'])
    params = {
        "wallet_address": request_args.get('wallet_address').lower(),
        "page_size": 100,
        "verified": "true"}

    if request_args.get("next_page_token"):
        params.update({"page_token": request_args.get("next_page_token")})
    
    headers = {'X-API-Key': os.environ["BLOCK_DAEMON_SECRET"] }
    
    url = f"https://svc.blockdaemon.com/nft/v1/{request_args.get('chain')}/mainnet/assets"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=headers) as resp:
            response  = await resp.json()

    if not response:
        return []

    result = []
    for token in response["data"]:
        contract_address = token.get("contract_address")
        res = await search_erc721_contract_address(app, "ethereum", contract_address)
        if res:
            token.update({"contract_name": res.get("name")})
        else:
            res = await search_erc1155_contract_address(app, "ethereum", contract_address)
            if res:
                token.update({"contract_name": res.get("name")})
        if token.get("contract_name") or token.get("name") != "":
            result.append(token)
    
    return {"result": result, "next_page_token": response['meta']['paging']['next_page_token']}

async def nft_balance_caching(app: object, caching_key: str, request_args: dict) -> any: 
    cache_valid = await cache_validity(app.config.REDIS_CLIENT, caching_key, 
                            app.config.CACHING_TTL['LEVEL_ZERO'])

    if not cache_valid:
        data = await fetch_nft_balance(app, request_args)
        if data: #only set cache when data is not empty
            await set_cache(app.config.REDIS_CLIENT, caching_key, data)
        return data
    result= await get_cache(app.config.REDIS_CLIENT, caching_key)
    return json.loads(result)




@USER_TOKEN_BALANCE_BP.get('nft_balances')
async def nft_balances(request):
    if not request.args.get('wallet_address'):
        raise CustomError("Wallet address is required")

    if not request.args.get('chain') in request.app.config["SUPPORTED_CHAINS"]:
        raise CustomError("chain is required")

    params = {
        "wallet_address": request.args.get('wallet_address').lower(),
        "page_size": 100,
        "verified": "true"}

    if request.args.get("next_page_token"):
        params.update({"page_token": request.args.get("next_page_token")})
    wallet_address = request.args.get('wallet_address')
    chain = request.args.get('chain')
    # await fetch_nft_balance(request.app, request.args, "ethereum")
  
    if not wallet_address:
        raise CustomError("Wallet address is required")
    
    if not chain:
        raise CustomError("chain is required")

    query_string: str = make_query_string(request.args, ["chain", "wallet_address", "next_page_token"])

    caching_key = f"{request.route.path}?{query_string}"
    logger.info(f"Here is the caching key {caching_key}")
    data = await nft_balance_caching(request.app, caching_key, request.args)
       
    return Response.success_response(data=data)