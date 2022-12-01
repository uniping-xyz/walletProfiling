import requests
import json
import asyncio
import aiohttp
from sanic import Blueprint
from utils.utils import Response
from utils.errors import CustomError
from utils.authorization import is_subscribed
from loguru import logger
from sanic.request import RequestParameters
from find_addresses.external_calls import blockdaemon_calls
from find_addresses.external_calls import luabase_floor_price
from find_addresses.external_calls import bq_token_stats
from caching.cache_utils import cache_validity, get_cache, set_cache, delete_cache

import re
from caching.cache_utils import cache_validity, get_cache, set_cache, delete_cache

TOKEN_STATS_BP = Blueprint("stats", url_prefix='/token', version=1)
NUMBER_OF_DAYS = 30

def make_query_string(request_args: dict, args_list: list) -> str:
    query_string = ""
    for (key, value) in request_args.items():
        if key in args_list:
            if type(value) == list:
                value = value[0]
            query_string += f"&{key}={value}"
    return query_string[1:] # to remove the first $ sign appened to the string

@TOKEN_STATS_BP.get('stats')
@is_subscribed()
async def stats(request):

    if not request.args.get("token_address") :
        raise CustomError("token_address is required ")

    if not request.args.get("chain") or  request.args.get("chain") not in ["ethereum", "polygon"]:
        raise CustomError("Chain is required and should be either ethereum or polygon")
    
    token_address = request.args.get("token_address")
    
    
    query_string: str = make_query_string(request.args, ["chain", "token_address"])
    if request.app.config.CACHING:
        caching_key = f"{request.route.path}?{query_string}"
        logger.info(f"Here is the caching key {caching_key}")
        data = await token_stats_caching(request.app, caching_key, request.args)
    else:
        data = await bq_token_stats.fetch_token_stats(request.app, request.args)
       
    # logger.success(result)
    # logger.success(f"Length of the result returned is {len(result)}")
    return Response.success_response(data=data)

async def token_stats_caching(app: object, caching_key: str, request_args: dict) -> any: 
    cache_valid = await cache_validity(app.config.REDIS_CLIENT, caching_key, 
                            app.config.CACHING_TTL['LEVEL_FIVE'])

    if not cache_valid:
        data = await bq_token_stats.fetch_token_stats(app, request_args)
        if data: #only set cache when data is not empty
            await set_cache(app.config.REDIS_CLIENT, caching_key, data)
        return data
    result= await get_cache(app.config.REDIS_CLIENT, caching_key)
    return json.loads(result)



@TOKEN_STATS_BP.get('metadata')
@is_subscribed()
async def token_metadata(request):
    if not request.args.get("token_address") :
        raise CustomError("token_address is required ")
    response = await blockdaemon_calls.get_nft_collection_details(request.args.get("token_address"))
    
    return Response.success_response(data=response)

#____________________________ floor_price of contract address ______________________________________


async def floor_price_caching(app: object, caching_key: str, caching_ttl:int, request_args: dict) -> any: 
    cache_valid = await cache_validity(app.config.REDIS_CLIENT, caching_key, caching_ttl)

    if not cache_valid:
        data = await luabase_floor_price.floor_price_per_day(request_args.get("token_address"), NUMBER_OF_DAYS)
        if data: #only set cache when data is not empty
            await set_cache(app.config.REDIS_CLIENT, caching_key, data)
        return data
    result= await get_cache(app.config.REDIS_CLIENT, caching_key)
    return json.loads(result)


@TOKEN_STATS_BP.get('floor_price')
@is_subscribed()
async def floor_price(request):
    caching_ttl =  request.app.config.CACHING_TTL['LEVEL_FIVE']
    query_string: str = make_query_string(request.args, ["chain", "token_address"])
    caching_key = f"{request.route.path}?{query_string}"
    
    if not request.args.get("token_address") :
        raise CustomError("token_address is required ")
    response = await floor_price_caching(request.app, caching_key, caching_ttl, request.args)
    return Response.success_response(data=response, days=NUMBER_OF_DAYS, caching_ttl=caching_ttl)
