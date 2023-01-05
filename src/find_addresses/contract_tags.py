import requests
import json
import asyncio
import aiohttp
from sanic import Blueprint
from utils.utils import Response
from utils.authorization import is_subscribed
from utils.errors import CustomError
from loguru import logger
import re
from caching.cache_utils import cache_validity, get_cache, set_cache, delete_cache
from find_addresses.external_calls import luabase_token_tags 

TOKEN_TAGS_BP = Blueprint("tags", url_prefix='/tags/', version=1)

def make_query_string(request_args: dict, args_list: list) -> str:
    query_string = ""
    for (key, value) in request_args.items():
        if key in args_list:
            if type(value) == list:
                value = value[0]
            query_string += f"&{key}={value}"
    return query_string[1:] # to remove the first $ sign appened to the string

async def tags_cache_validity(app: object, caching_key: str, request_args: dict)-> object:
    CACHE_EXPIRY = app.config.CACHING_TTL['LEVEL_SIX']
    tags_cache_validity  = await cache_validity(app.config.REDIS_CLIENT, caching_key, CACHE_EXPIRY)
    if not tags_cache_validity:
        eth_tags = await luabase_token_tags.eth_all_tags()
        await set_cache(app.config.REDIS_CLIENT, caching_key, [e["label"] for e in eth_tags])
        return [e["label"] for e in eth_tags]
    data = await get_cache(app.config.REDIS_CLIENT,caching_key)
    return json.loads(data)


@TOKEN_TAGS_BP.get('find_tags')
@is_subscribed()
async def find_tags(request):

    if  request.args.get("chain") not in request.app.config.SUPPORTED_CHAINS:
        raise CustomError("chain not suported")

    if  request.args.get("query"):
        query = f".*{request.args.get('query')}"
    else:
        query = f".*"
    request.args["tag"] = True #this is just to make keys unique in redis

    r = re.compile(query)

    query_string: str = make_query_string(request.args, ["chain", "tag"])

    caching_key = f"{request.route.path}?{request.query_string}"
    if request.app.config.CACHING:
        caching_key = f"{request.route.path}?{query_string}"
        logger.info(f"Here is the caching key {caching_key}")
        data = await tags_cache_validity(request.app, caching_key, request.args)
    else:
        data = await  luabase_token_tags.eth_all_tags()

    result = list(filter(r.match, data)) # Read Note below

    return Response.success_response(data=result)


async def fetch_all_tag_contracts(app, request_args, caching_key):
    data = await luabase_token_tags.get_tagged_ethereum_contracts(request_args.get("tag"))
    await set_cache(app.config.REDIS_CLIENT, caching_key, data)
    return json.loads(data)

async def tags_contracts_cache_validity(request, caching_key, request_args, cache_ttl) -> object:
    
    data = await get_cache(request.app.config.REDIS_CLIENT, caching_key)
    if data:
        tags_contracts_cache  = await cache_validity(request.app.config.REDIS_CLIENT, caching_key, cache_ttl)
        if not tags_contracts_cache:
            request.app.add_task(fetch_all_tag_contracts(request.app, request_args, caching_key))
        return json.loads(data)
    logger.success("Cache is empty for this All tags request")
    data = await fetch_all_tag_contracts(request.app, request_args, caching_key)
    return data

"""
This fetches all the contracts that are associated with a tag on the ethereum blockchain
"""
@TOKEN_TAGS_BP.get('find_tagged_contracts')
@is_subscribed()
async def find_tagged_contracts(request):
    CACHE_TTL = request.app.config.CACHING_TTL['LEVEL_EIGHT']

    if  request.args.get("chain") not in request.app.config.SUPPORTED_CHAINS:
        raise CustomError("chain not suported")

    if  not request.args.get("tag"):
        raise CustomError("Tag is required")
    query_string: str = make_query_string(request.args, ["chain", "tag"])

    caching_key = f"{request.route.path}?{query_string}"
    logger.info(f"Here is the caching key {caching_key}")
    data = await tags_contracts_cache_validity(request.app, caching_key, request.args)
    return Response.success_response(data=data)

async def fetch_all_tags(app, caching_key):
    data = await luabase_token_tags.get_all_ethereum_tags_with_contracts()
    await set_cache(app.config.REDIS_CLIENT, caching_key, data)
    return json.loads(data)


async def all_tags_contracts_cache_validity(request, caching_key, cache_ttl) -> object:
    data = await get_cache(request.app.config.REDIS_CLIENT, caching_key)
    if data:
        logger.info("Tags have been foudn and loding from cache")
        tags_contracts_cache  = await cache_validity(request.app.config.REDIS_CLIENT, caching_key, cache_ttl)
        if not tags_contracts_cache:
            request.app.add_task(fetch_all_tags(request.app, caching_key))
        return json.loads(data)
    logger.success("Cache is empty for this All tags request")
    data = await fetch_all_tags(request.app, caching_key)
    return data

"""
This fetches all the tags on the ethereum blockchain
"""
@TOKEN_TAGS_BP.get('all_tags')
#@is_subscribed()
async def all_tags(request):
    CACHE_TTL = request.app.config.CACHING_TTL['LEVEL_FIVE']

    if  request.args.get("chain") not in request.app.config.SUPPORTED_CHAINS:
        raise CustomError("chain not suported")

    query_string: str = make_query_string(request.args, ["chain"])
    caching_key = f"{request.route.path}?{query_string}?all_tags"
    logger.info(caching_key)

    data = await all_tags_contracts_cache_validity(request.app, caching_key, CACHE_TTL)
    return Response.success_response(data=data)

# async def most_popular_token_caching(request: object, caching_key: str, request_args: dict, caching_ttl: int) -> any:
#     await check_coingecko_tokens_staleness(request.app)
#     await check_blockDaemon_tokens_staleness(request.app)
#     result= await get_cache(request.app.config.REDIS_CLIENT, caching_key)
#     if result:
#         logger.info("result has been found and loading it from cached")
#         cache_valid = await cache_validity(request.app.config.REDIS_CLIENT, caching_key, caching_ttl)
#         if not cache_valid:
#             logger.warning("Cache expired fetching new data")
#             request.app.add_task(fetch_data(request.app, request_args, caching_key))
#         return json.loads(result)
#     logger.success("Cache is empty for this request")
#     data = await fetch_data(request.app, request_args, caching_key)
#     return data

