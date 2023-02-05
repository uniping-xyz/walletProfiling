import requests
import json
import asyncio
import aiohttp
from sanic.request import RequestParameters
from sanic import Blueprint
from utils.utils import Response
from utils.errors import CustomError
from utils.authorization import is_subscribed
from loguru import logger
from caching.cache_utils import cache_validity, get_cache, set_cache, delete_cache
from .ethereum.eth_erc20 import eth_erc20_top_tokens
from .ethereum.eth_erc721 import eth_erc721_top_tokens
from .ethereum.eth_erc1155 import eth_erc1155_top_tokens


MOST_POPULAR_BP = Blueprint("most_popular", url_prefix='/most_popular/tokens', version=1)


def make_query_string(request_args: dict) -> str:
    query_string = ""
    for (key, value) in request_args.items():
        if type(value) == list:
            value = value[0]
        query_string += f"&{key}={value}"
    return query_string[1:] # to remove the first $ sign appened to the string

async def fetch_data(app: object, request_args: RequestParameters, caching_key: str) -> any:
    if request_args.get("erc_type") ==  "ERC20":
        results = await  eth_erc20_top_tokens(  
                        request_args.get("number_of_days"), 
                        request_args.get("offset"), 
                        request_args.get("limit"))
     
    elif request_args.get("erc_type") ==  "ERC721":
       results = await  eth_erc721_top_tokens(  
                        request_args.get("number_of_days"), 
                        request_args.get("offset"), 
                        request_args.get("limit"))
    else:
        results = await  eth_erc1155_top_tokens(  
                        request_args.get("number_of_days"), 
                        request_args.get("offset"), 
                        request_args.get("limit"))
    
    await set_cache(app.config.REDIS_CLIENT, caching_key, results)
    return results


async def most_popular_token_caching(request: object, caching_key: str, request_args: dict, caching_ttl: int) -> any:
    # await check_coingecko_tokens_staleness(request.app)
    # await check_blockDaemon_tokens_staleness(request.app)
    result= await get_cache(request.app.config.REDIS_CLIENT, caching_key)
    logger.info("result in cache")
    logger.info(result)
    if result:
        if json.loads(result):
            logger.info("result has been found and loading it from cached")
            cache_valid = await cache_validity(request.app.config.REDIS_CLIENT, caching_key, caching_ttl)
            if not cache_valid:
                logger.warning("Cache expired fetching new data")
                request.app.add_task(fetch_data(request.app, request_args, caching_key))
            return json.loads(result)
    logger.success("Cache is empty for this request")
    data = await fetch_data(request.app, request_args, caching_key)
    return data

@MOST_POPULAR_BP.get('<chain>/most_popular')
# @is_subscribed()
async def most_popular(request, chain):
    CACHE_EXPIRY = request.app.config.CACHING_TTL['LEVEL_FOUR']

    if chain not in request.app.config.SUPPORTED_CHAINS:
        raise CustomError("chain not suported")

    if not request.args.get("erc_type"):
        raise CustomError("ERC Type is required")

    if not request.args.get("erc_type") in ["ERC20", "ERC721", "ERC1155"]:
        raise CustomError("ERC Type is not valid")


    if not request.args.get("number_of_days"):
        request.args["number_of_days"] = [7]
    
    if not request.args.get("limit"):
        request.args["limit"] = [20]
    
    if not request.args.get("offset"):
        request.args["offset"] = [0]

        
    query_string: str = make_query_string(request.args)
    caching_key = f"{request.route.path}?{query_string}"
    logger.info(f"Here is the caching key {caching_key}")
    data = await most_popular_token_caching(request, caching_key, request.args, CACHE_EXPIRY)
    
    return Response.success_response(data=data, caching_ttl=CACHE_EXPIRY)
