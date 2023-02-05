import json

from sanic import Blueprint
from utils.utils import Response
from utils.errors import CustomError
from loguru import logger
from sanic.request import RequestParameters
from .ethereum.eth_erc721_1155_stats import get_nft_metadata, get_nft_sales_on_platforms
from find_addresses.external_calls import bq_token_stats
from caching.cache_utils import cache_validity, get_cache, set_cache, delete_cache

import re
from caching.cache_utils import cache_validity, get_cache, set_cache, delete_cache

TOKEN_STATS_BP = Blueprint("stats", url_prefix='/token', version=1)
NUMBER_OF_DAYS = 10

def make_query_string(request_args: dict, args_list: list) -> str:
    query_string = ""
    for (key, value) in request_args.items():
        if key in args_list:
            if type(value) == list:
                value = value[0]
            query_string += f"&{key}={value}"
    return query_string[1:] # to remove the first $ sign appened to the string

@TOKEN_STATS_BP.get('<chain>/stats')
async def stats(request, chain):

    if not request.args.get("token_address") :
        raise CustomError("token_address is required ")

    if not chain in ["ethereum", "polygon"]:
        raise CustomError("Chain is required and should be either ethereum or polygon")
    request.args["chain"] = chain
    token_address = request.args.get("token_address")
    
    
    query_string: str = make_query_string(request.args, ["chain", "token_address"])
    caching_key = f"{query_string}"
    logger.info(f"Here is the caching key {caching_key}")
    data = await token_stats_caching(request.app, caching_key, request.args)
       
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


@TOKEN_STATS_BP.get('<chain>/metadata')
async def token_metadata(request, chain):
    if not request.args.get("token_address") :
        raise CustomError("token_address is required ")
    response = await get_nft_metadata(request.args.get("token_address"))
    return Response.success_response(data=response)

#____________________________ floor_price of contract address ______________________________________


async def nft_sales_caching(app: object, caching_key: str, caching_ttl:int, request_args: dict) -> any: 
    cache_valid = await cache_validity(app.config.REDIS_CLIENT, caching_key, caching_ttl)

    if not cache_valid:
        data = await get_nft_sales_on_platforms(request_args.get("token_address"), 30)
        if data: #only set cache when data is not empty
            await set_cache(app.config.REDIS_CLIENT, caching_key, data)
        return data
    result= await get_cache(app.config.REDIS_CLIENT, caching_key)
    return json.loads(result)


@TOKEN_STATS_BP.get('<chain>/nft_sales')
async def nft_sales(request, chain):
    caching_ttl =  request.app.config.CACHING_TTL['LEVEL_THREE']
    request.args["chain"] = chain
    query_string: str = make_query_string(request.args, ["chain", "token_address"])
    caching_key = f"{request.route.path}?{query_string}"
    
    if not request.args.get("token_address") :
        raise CustomError("token_address is required ")
    response = await nft_sales_caching(request.app, caching_key, caching_ttl, request.args)
    return Response.success_response(data=response, days=60, caching_ttl=caching_ttl)