import requests
import json
import asyncio
import aiohttp
from sanic import Blueprint
from utils.utils import Response
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
    response = requests.request("POST", url, json=payload, headers=headers)
    data = response.json() 
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
    response = requests.request("POST", url, json=payload, headers=headers)
    data = response.json()
    return data["data"]

async def tags_cache_validity(app: object, cache_validity_hours: int) -> object:
    for chain in app.config.SUPPORTED_CHAINS:
        tags_cache_validity  = await cache_validity(app.config.REDIS_CLIENT, f"{chain}-tags", cache_validity_hours)
        if not tags_cache_validity:
            eth_tags = await get_ethereum_tags(app.config.LUABASE_API_KEY)
            await set_cache(app.config.REDIS_CLIENT, f"{chain}-tags", [e["label"] for e in eth_tags], cache_validity_hours)
            return [e["label"] for e in eth_tags]
    data = await get_cache(app.config.REDIS_CLIENT,f"{chain}-tags")
    return json.loads(data)

@TOKEN_TAGS_BP.get('find_tags')
async def find_tags(request):

    if  request.args.get("chain") not in request.app.config.SUPPORTED_CHAINS:
        raise CustomError("chain not suported")

    if  request.args.get("query"):
        query = f".*{request.args.get('query')}"
    else:
        query = f".*"


    r = re.compile(query)

    data = await tags_cache_validity(request.app, request.app.config.CACHING_TTL['LEVEL_EIGHT'])
    result = list(filter(r.match, data)) # Read Note below

    return Response.success_response(data=result)

@TOKEN_TAGS_BP.get('find_tagged_contracts')
async def find_tagged_contracts(request):

    if  request.args.get("chain") not in request.app.config.SUPPORTED_CHAINS:
        raise CustomError("chain not suported")

    if  not request.args.get("tag"):
        raise CustomError("Tag is required")

    caching_key = f"{request.route.path}?{request.query_string}"
    if request.app.config.CACHING:

        cache_valid = await cache_validity(request.app.config.REDIS_CLIENT, caching_key, 
                            request.app.config.CACHING_TTL['LEVEL_EIGHT'])
        if not cache_valid:
            result = await get_tagged_ethereum_contracts(request.app.config.LUABASE_API_KEY, request.args.get("tag"))
            await set_cache(request.app.config.REDIS_CLIENT, caching_key, result)
            return result
        cached_result= await get_cache(request.app.config.REDIS_CLIENT, caching_key)
        return json.loads(cached_result)
    else:
        result = await get_tagged_ethereum_contracts(request.app.config.LUABASE_API_KEY, request.args.get("tag"))
    return Response.success_response(data=result)



async def tags_cache_validity(app: object, cache_validity_hours: int) -> object:
    for chain in app.config.SUPPORTED_CHAINS:
        tags_cache_validity  = await cache_validity(app.config.REDIS_CLIENT, f"{chain}/tags", cache_validity_hours)
        if not tags_cache_validity:
            eth_tags = await get_ethereum_tags(app.config.LUABASE_API_KEY)
            await set_cache(app.config.REDIS_CLIENT, f"{chain}/tags", [e["label"] for e in eth_tags])
            return [e["label"] for e in eth_tags]
    data = await get_cache(app.config.REDIS_CLIENT,f"{chain}/tags")
    return json.loads(data)


