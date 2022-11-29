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
from populate_data.populate_coingecko import check_coingecko_tokens_staleness
from populate_data.populate_blockdaemon import  check_blockDaemon_tokens_staleness
from find_addresses.db_calls.erc20.ethereum import search_contract_address as erc20_eth_search
from find_addresses.db_calls.erc721.ethereum import search_contract_address as erc721_eth_search
from find_addresses.db_calls.erc1155.ethereum import search_contract_address as erc1155_eth_search
from find_addresses.external_calls import alchemy_calls
from find_addresses.external_calls import luabase_wallet_stats, luabase_contract_search
import re
from caching.cache_utils import cache_validity, get_cache, set_cache, delete_cache
from find_addresses.external_calls import blockdaemon_calls

USER_TOKEN_BALANCE_BP = Blueprint("wallet", url_prefix='/wallet', version=1)

def make_query_string(request_args: dict, args_list: list) -> str:
    query_string = ""
    for (key, value) in request_args.items():
        if key in args_list:
            if type(value) == list:
                value = value[0]
            query_string += f"&{key}={value}"
    return query_string[1:] # to remove the first $ sign appened to the string




async def erc20_balance_caching(app: object, caching_key: str, request_args: dict) -> any: 
    cache_valid = await cache_validity(app.config.REDIS_CLIENT, caching_key, 
                            app.config.CACHING_TTL['LEVEL_FOUR'])

    if not cache_valid:
        data = await get_erc20_balance(app, request_args)
        if data: #only set cache when data is not empty
            await set_cache(app.config.REDIS_CLIENT, caching_key, data)
        return data
    result= await get_cache(app.config.REDIS_CLIENT, caching_key)
    return json.loads(result)


async def get_erc20_balance(app: object, request_args: RequestParameters) -> list:
    await check_coingecko_tokens_staleness(app)
    await check_blockDaemon_tokens_staleness(app) ##this checks if the coingecko token list in db is not older than 5 hours
    response = await alchemy_calls.erc20_wallet_balance(os.environ["ETH_WALLET_BALANCE_URL"],  request_args.get("wallet_address"))
    result = []

    for e in response["result"]["tokenBalances"]:
        contract_address = e["contractAddress"]
        token_balance = e["tokenBalance"]
        contract_name =  await erc20_eth_search(app, contract_address)
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

@USER_TOKEN_BALANCE_BP.get('erc20_balances')
@is_subscribed()
async def erc20_balances(request):
    wallet_address = request.args.get('wallet_address')
    chain = request.args.get('chain')

    # await fetch_nft_balance(request.app, request.args, "ethereum")
  
    if not wallet_address:
        raise CustomError("Wallet address is required")
    
    if not chain:
        raise CustomError("chain is required")

    query_string: str = make_query_string(request.args, ["chain", "erc20", "wallet_address"])

    caching_key = f"{request.route.path}?{query_string}"
    logger.info(f"Here is the caching key {caching_key}")
    data = await erc20_balance_caching(request.app, caching_key, request.args)
       
    return Response.success_response(data=data)


"""
Get assets related to a wallet address from Block Daemon
"""
async def fetch_nft_balance(app, request_args) -> list:
    response = await blockdaemon_calls.get_eth_nft_balance(request_args.get("wallet_address"), request_args.get("next_page_token"))

    if not response:
        return []

    result = []
    for token in response["data"]:
        contract_address = token.get("contract_address")
        res = await erc721_eth_search(app, contract_address)
        if res:
            token.update({"contract_name": res.get("name")})
        else:
            res = await erc1155_eth_search(app, contract_address)
            if res:
                token.update({"contract_name": res.get("name")})
        if token.get("contract_name") or token.get("name") != "":
            result.append(token)
    
    return {"result": result, "next_page_token": response['meta']['paging']['next_page_token']}

async def nft_balance_caching(app: object, caching_key: str, request_args: dict) -> any: 
    cache_valid = await cache_validity(app.config.REDIS_CLIENT, caching_key, 
                            app.config.CACHING_TTL['LEVEL_FOUR'])

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


@USER_TOKEN_BALANCE_BP.get('txs_per_day')
async def txs_per_day(request):
    if not request.args.get('wallet_address'):
        raise CustomError("Wallet address is required")

    if not request.args.get('chain') in request.app.config["SUPPORTED_CHAINS"]:
        raise CustomError("chain is required")

    wallet_address = request.args.get('wallet_address')
    chain = request.args.get('chain')
    res = await luabase_wallet_stats.wallet_txs_per_day(wallet_address)
    # await fetch_nft_balance(request.app, request.args, "ethereum")
         
    return Response.success_response(data=res)

@USER_TOKEN_BALANCE_BP.get('txs')
async def txs(request):
    if not request.args.get('wallet_address'):
        raise CustomError("Wallet address is required")

    if not request.args.get('chain') in request.app.config["SUPPORTED_CHAINS"]:
        raise CustomError("chain is required")

    wallet_address = request.args.get('wallet_address')
    chain = request.args.get('chain')
    res = await luabase_wallet_stats.wallet_txs(wallet_address)
    # await fetch_nft_balance(request.app, request.args, "ethereum")
         
    return Response.success_response(data=res)

@USER_TOKEN_BALANCE_BP.get('most_interactions')
async def txs(request):
    if not request.args.get('wallet_address'):
        raise CustomError("Wallet address is required")

    if not request.args.get('chain') in request.app.config["SUPPORTED_CHAINS"]:
        raise CustomError("chain is required")

    wallet_address = request.args.get('wallet_address')
    chain = request.args.get('chain')
    outgoing = await luabase_wallet_stats.wallet_most_outgoing_interactions(wallet_address, 180)
    incoming = await luabase_wallet_stats.wallet_most_incoming_interactions(wallet_address, 180)

    # await fetch_nft_balance(request.app, request.args, "ethereum")
         
    return Response.success_response(data={"outgoing": outgoing, "incoming": incoming})

# async def fetch_contract_standard_type(app, contract_address):
#     result = erc20_eth_search(app, contract_address):

#     response = await luabase_contract_search.search_contract_contracts_table(request_args.get("contract_address"))
#     if not response:
#         logger.error(f'{request_args.get("contract_address")} ERC_STANDARD=[{None }]')
#         return None   
#     for (key, standard) in [("is_erc20", "erc20"), ("is_erc721", "erc721"), ("is_erc1155", "erc1155")]:
#         if response[0].get(key):
#             logger.success(f'{request_args.get("contract_address")} ERC_STANDARD=[{standard}]')
#             return standard
#     logger.warning("Probabaly a Proxy contract found")

#     _response = await find_standard_if_proxy(request_args.get("contract_address"))
#     logger.success(f'{request_args.get("contract_address")} ERC_STANDARD=[{_response }]')
#     if _response:
#         return _response
#     logger.error(f'{request_args.get("contract_address")} ERC_STANDARD=[{None }]')
#     return None