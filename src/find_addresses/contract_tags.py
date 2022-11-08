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

TOKEN_TAGS_BP = Blueprint("tags", url_prefix='/tags/', version=1)



async def get_ethereum_tags(lubabase_api_key):
    url = "https://q.luabase.com/run"

    payload = {
    "block": {
        "data_uuid": "958a4cdf11684438942e591e9bdb6e18"
    },
    "api_key": lubabase_api_key,
    "parameters": {
        "label": {
            "value": "defi",
            "type": "value"
        }
    }
    }
    headers = {"content-type": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            data  = await resp.json()
    return data["data"]



async def get_tagged_ethereum_contracts(luabase_api_key, tag):
    url = "https://q.luabase.com/run"

    payload = {
    "block": {
        "data_uuid": "99310c5e8af9418197027ba9c8af3e24",
        "details": {
            "parameters": {
                "label": {
                    "value": tag,
                    "type": "value"
                }
            }
        }
    },
    "api_key": luabase_api_key
    }
    headers = {"content-type": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            data  = await resp.json()
    return data["data"]


async def tags_cache_validity(app: object, caching_key: str, request_args: dict)-> object:
    CACHE_EXPIRY = app.config.CACHING_TTL['LEVEL_FIVE']
    tags_cache_validity  = await cache_validity(app.config.REDIS_CLIENT, caching_key, CACHE_EXPIRY)
    if not tags_cache_validity:
        eth_tags = await get_ethereum_tags(app.config.LUABASE_API_KEY)
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
        data = await  get_ethereum_tags(request.app.config.LUABASE_API_KEY)

    result = list(filter(r.match, data)) # Read Note below

    return Response.success_response(data=result)


def make_query_string(request_args: dict, args_list: list) -> str:
    query_string = ""
    for (key, value) in request_args.items():
        if key in args_list:
            if type(value) == list:
                value = value[0]
            query_string += f"&{key}={value}"
    return query_string[1:] # to remove the first $ sign appened to the string

async def tags_contracts_cache_validity(app: object, caching_key: str, request_args: dict) -> object:
    CACHE_EXPIRY = app.config.CACHING_TTL['LEVEL_EIGHT']
    tags_contracts_cache  = await cache_validity(app.config.REDIS_CLIENT, caching_key, CACHE_EXPIRY)
    if not tags_contracts_cache:
        data = await get_tagged_ethereum_contracts(app.config.LUABASE_API_KEY, request_args.get("tag"))
        await set_cache(app.config.REDIS_CLIENT, caching_key, data)
        return data
    data = await get_cache(app.config.REDIS_CLIENT, caching_key)
    return json.loads(data)




@TOKEN_TAGS_BP.get('find_tagged_contracts')
@is_subscribed()
async def find_tagged_contracts(request):

    if  request.args.get("chain") not in request.app.config.SUPPORTED_CHAINS:
        raise CustomError("chain not suported")

    if  not request.args.get("tag"):
        raise CustomError("Tag is required")
    query_string: str = make_query_string(request.args, ["chain", "tag"])

    caching_key = f"{request.route.path}?{request.query_string}"
    if request.app.config.CACHING:
        caching_key = f"{request.route.path}?{query_string}"
        logger.info(f"Here is the caching key {caching_key}")
        data = await tags_contracts_cache_validity(request.app, caching_key, request.args)
    else:
        data = await  get_tagged_ethereum_contracts(request.app.config.LUABASE_API_KEY, request.args.get("tag"))
    return Response.success_response(data=data)
