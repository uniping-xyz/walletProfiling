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
from find_addresses.external_calls import luabase_trending
from caching.cache_utils import cache_validity, get_cache, set_cache, delete_cache
from find_addresses.db_calls.erc20.ethereum import search_contract_address as erc20_eth_search
from find_addresses.db_calls.erc721.ethereum import search_contract_address as erc721_eth_search
from find_addresses.db_calls.erc1155.ethereum import search_contract_address as erc1155_eth_search

MOST_POPULAR_BP = Blueprint("most_popular", url_prefix='/most_popular/tokens', version=1)


def make_query_string(request_args: dict) -> str:
    query_string = ""
    for (key, value) in request_args.items():
        if type(value) == list:
            value = value[0]
        query_string += f"&{key}={value}"
    return query_string[1:] # to remove the first $ sign appened to the string

@MOST_POPULAR_BP.get('most_popular')
@is_subscribed()
async def most_popular(request):
    
    if request.args.get("chain") not in request.app.config.SUPPORTED_CHAINS:
        raise CustomError("chain not suported")

    if not request.args.get("erc_type"):
        raise CustomError("ERC Type is required")

    if not request.args.get("erc_type") in ["ERC20", "ERC721", "ERC1155"]:
        raise CustomError("ERC Type is not valid")


    if not request.args.get("number_of_days"):
        request.args["number_of_days"] = [3]
    
    if not request.args.get("limit"):
        request.args["limit"] = [20]
    
    if not request.args.get("offset"):
        request.args["offset"] = [0]

        

    query_string: str = make_query_string(request.args)


    if request.app.config.CACHING:
        caching_key = f"{request.route.path}?{query_string}"
        logger.info(f"Here is the caching key {caching_key}")
        data = await most_popular_token_caching(request.app, caching_key, request.args)
    else:
        data = await fetch_data(request.app, request.args)
  
    result = []
    for row in data:
        result.append({
                "total_transactions": row['total_transactions'],
                "contract_address": row['contract_address'],
                "name": row['name'],
                "symbol": row['symbol']
        }) 
    return Response.success_response(data=result)


async def most_popular_token_caching(app: object, caching_key: str, request_args: dict) -> any: 
    cache_valid = await cache_validity(app.config.REDIS_CLIENT, caching_key, 
                            app.config.CACHING_TTL['LEVEL_ZERO'])

    if not cache_valid:
        data = await fetch_data(app, request_args)
        await set_cache(app.config.REDIS_CLIENT, caching_key, data)
        return data
    result= await get_cache(app.config.REDIS_CLIENT, caching_key)
    return json.loads(result)

async def fetch_data(app: object, request_args: RequestParameters) -> any:
    if request_args.get("erc_type") ==  "ERC20":
        results = await luabase_trending.topERC20(app.config.LUABASE_API_KEY,  
                        request_args.get("chain"), request_args.get("limit"), 
                        request_args.get("offset"), request_args.get("number_of_days"))
        for e in results:
            if not e["name"]:
                res = await erc20_eth_search(app, e["contract_address"])
                if res:
                    e.update({"name": res.get("name")})


    elif request_args.get("erc_type") ==  "ERC721":
        results = await luabase_trending.topERC721(app.config.LUABASE_API_KEY,  
                        request_args.get("chain"), request_args.get("limit"), 
                        request_args.get("offset"), request_args.get("number_of_days")) 
        for e in results:
            if not e["name"]:
                logger.info(f"OLD {e}")
                res = await erc721_eth_search(app, e["contract_address"])
                if res:
                    e.update({"name": res.get("name")})
    else:
        results = await luabase_trending.topERC1155(app.config.LUABASE_API_KEY,  
                        request_args.get("chain"), request_args.get("limit"), 
                        request_args.get("offset"), request_args.get("number_of_days"))
        for e in results:
            if not e["name"]:
                res = await erc1155_eth_search(app, e["contract_address"])
                if res:
                    e.update({"name": res.get("name")})
    return results