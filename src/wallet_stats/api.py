


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
import re
from caching.cache_utils import cache_validity, get_cache, set_cache, delete_cache
from find_addresses.external_calls import blockdaemon_calls
from .ethereum.nft_transfers import eth_wallet_nft_transfers
from .ethereum.erc20_transfers import eth_wallet_erc20_transfers
from .ethereum.erc20_balance import eth_erc20_balance
from .ethereum.nft_balances import eth_nft_balance

from .ethereum.txs_per_day import eth_wallet_tx_per_day

USER_TOKEN_BALANCE_BP = Blueprint("wallet", url_prefix='/wallet', version=1)

NUMBER_OF_DAYS = 30

def make_query_string(request_args: dict, args_list: list) -> str:
    query_string = ""
    for (key, value) in request_args.items():
        if key in args_list:
            if type(value) == list:
                value = value[0]
            query_string += f"&{key}={value}"
    return query_string[1:]

async def nft_transfers_caching(app: object, caching_key: str, caching_ttl:int, request_args: dict) -> any: 
    cache_valid = await cache_validity(app.config.REDIS_CLIENT, caching_key, caching_ttl)

    if not cache_valid:
        data = await eth_wallet_nft_transfers(request_args.get("wallet_address"), NUMBER_OF_DAYS)
        if data:
            await set_cache(app.config.REDIS_CLIENT, caching_key, data)
        return data
    result= await get_cache(app.config.REDIS_CLIENT, caching_key)
    return json.loads(result)

@USER_TOKEN_BALANCE_BP.get('<chain>/nft_transfers')
async def txs(request, chain):

    caching_ttl =  request.app.config.CACHING_TTL['LEVEL_THREE']

    if not request.args.get('wallet_address'):
        raise CustomError("Wallet address is required")

    if chain in request.app.config["SUPPORTED_CHAINS"]:
        raise CustomError("chain is required")
    request.args["chain"] = chain


    query_string: str = make_query_string(request.args, ["chain", "wallet_address"])
    caching_key = f"{request.route.path}?{query_string}"

    data = await nft_transfers_caching(request.app, caching_key, caching_ttl, request.args)
         
    return Response.success_response(data=data, caching_ttl=caching_ttl, days=NUMBER_OF_DAYS)


async def erc20_transfers_caching(app: object, caching_key: str, caching_ttl:int, request_args: dict) -> any: 
    cache_valid = await cache_validity(app.config.REDIS_CLIENT, caching_key, caching_ttl)

    if not cache_valid:
        data = await eth_wallet_erc20_transfers(request_args.get("wallet_address"), NUMBER_OF_DAYS)
        if data:
            await set_cache(app.config.REDIS_CLIENT, caching_key, data)
        return data
    result= await get_cache(app.config.REDIS_CLIENT, caching_key)
    return json.loads(result)

@USER_TOKEN_BALANCE_BP.get('<chain>/erc20_transfers')
async def txs(request, chain):

    caching_ttl =  request.app.config.CACHING_TTL['LEVEL_THREE']

    if not request.args.get('wallet_address'):
        raise CustomError("Wallet address is required")

    if not chain in request.app.config["SUPPORTED_CHAINS"]:
        raise CustomError("chain is required")
    request.args["chain"] = chain


    query_string: str = make_query_string(request.args, ["chain", "wallet_address"])
    caching_key = f"{query_string}"

    data = await erc20_transfers_caching(request.app, caching_key, caching_ttl, request.args)
         
    return Response.success_response(data=data, caching_ttl=caching_ttl, days=NUMBER_OF_DAYS)

async def txs_per_day_caching(app: object, caching_key: str, caching_ttl:int, request_args: dict) -> any:
    cache_valid = await cache_validity(app.config.REDIS_CLIENT, caching_key, caching_ttl)

    if not cache_valid:
        data = await eth_wallet_tx_per_day(request_args.get("wallet_address"), NUMBER_OF_DAYS)
        if data: #only set cache when data is not empty
            await set_cache(app.config.REDIS_CLIENT, caching_key, data)
        return data
    result= await get_cache(app.config.REDIS_CLIENT, caching_key)
    return json.loads(result)


@USER_TOKEN_BALANCE_BP.get('<chain>/txs_per_day')
async def txs_per_day(request, chain):
    caching_ttl =  request.app.config.CACHING_TTL['LEVEL_THREE']

    if not request.args.get('wallet_address'):
        raise CustomError("Wallet address is required")

    if not chain in request.app.config["SUPPORTED_CHAINS"]:
        raise CustomError("chain is required")
    request.args["chain"] = chain

    wallet_address = request.args.get('wallet_address')
    chain = request.args.get('chain')
    query_string: str = make_query_string(request.args, ["chain", "wallet_address"])
    caching_key = f"{request.route.path}?{query_string}"
    logger.info(f"Here is the caching key for Txs/Day  by wallet adress {caching_key}")

    data = await txs_per_day_caching(request.app, caching_key, caching_ttl, request.args)
    # await fetch_nft_balance(request.app, request.args, "ethereum")
         
    return Response.success_response(data=data, caching_ttl=caching_ttl, days=NUMBER_OF_DAYS)


async def erc20_balance_caching(app: object, caching_key: str, caching_ttl: int, request_args: dict) -> any: 
    cache_valid = await cache_validity(app.config.REDIS_CLIENT, caching_key, caching_ttl)

    if not cache_valid:
        data = await eth_erc20_balance(app, request_args)
        if data: #only set cache when data is not empty
            await set_cache(app.config.REDIS_CLIENT, caching_key, data)
        return data
    result= await get_cache(app.config.REDIS_CLIENT, caching_key)
    return json.loads(result)


@USER_TOKEN_BALANCE_BP.get('<chain>/erc20_balances')
@is_subscribed()
async def erc20_balances(request, chain):
    caching_ttl =  request.app.config.CACHING_TTL['LEVEL_THREE']

    wallet_address = request.args.get('wallet_address')
  
    if not wallet_address:
        raise CustomError("Wallet address is required")
    
    if not chain:
        raise CustomError("chain is required")
    request.args["chain"] = chain

    query_string: str = make_query_string(request.args, ["chain", "erc20", "wallet_address"])

    caching_key = f"{request.route.path}?{query_string}"
    logger.info(f"Here is the caching key {caching_key}")
    data = await erc20_balance_caching(request.app, caching_key, caching_ttl, request.args)
       
    return Response.success_response(data=data, caching_ttl=caching_ttl, days=0)

async def nft_balance_caching(app: object, caching_key: str, caching_ttl:int, request_args: dict) -> any: 
    cache_valid = await cache_validity(app.config.REDIS_CLIENT, caching_key, caching_ttl)

    if not cache_valid:
        data = await eth_nft_balance(app, request_args)
        if data: #only set cache when data is not empty
            await set_cache(app.config.REDIS_CLIENT, caching_key, data)
        return data
    result = await get_cache(app.config.REDIS_CLIENT, caching_key)
    return json.loads(result)


@USER_TOKEN_BALANCE_BP.get('<chain>/nft_balances')
async def nft_balances(request, chain):
    caching_ttl =  request.app.config.CACHING_TTL['LEVEL_THREE']

    if not chain in request.app.config["SUPPORTED_CHAINS"]:
        raise CustomError("chain is required")

    wallet_address = request.args.get('wallet_address')
    request.args["chain"] = chain

    # await fetch_nft_balance(request.app, request.args, "ethereum")
  
    if not wallet_address:
        raise CustomError("Wallet address is required")
    
    
    query_string: str = make_query_string(request.args, ["chain", "wallet_address", "next_page_token"])

    caching_key = f"{request.route.path}?{query_string}"
    logger.info(f"Here is the caching key {caching_key}")
    data = await nft_balance_caching(request.app, caching_key, caching_ttl, request.args)
       
    return Response.success_response(data=data, caching_ttl=caching_ttl, days=0)

@USER_TOKEN_BALANCE_BP.get('<chain>/test')
async def test(request, chain):
    print (request.route.path)
    print (dir(request.route))