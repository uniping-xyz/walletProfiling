
from xml.dom.minidom import Document
import json
import asyncio
import aiohttp
from sanic import Blueprint
from utils.utils import Response
from utils.errors import CustomError
from utils.authorization import is_subscribed
from loguru import logger
from eth_utils import to_checksum_address
from sanic.request import RequestParameters

from caching.cache_utils import cache_validity, get_cache, set_cache
from populate_data.populate_blockdaemon import  check_blockDaemon_tokens_staleness, \
            populate_erc721_blockdaemon, populate_erc1155_blockdaemon

from .ethereum.eth_search_contract import  eth_contract_details, eth_contract_on_text

TOKEN_SEARCH_BP = Blueprint("search", url_prefix='/search/tokens', version=1)

"""
Based on the contract address, this API gives you the standard of the contract address
even if that contract address is a proxy
Also gives the the top holders of the token
"""


async def contract_standard_type_caching(app: object, caching_key: str, request_args: dict) -> any: 
    cache_valid = await cache_validity(app.config.REDIS_CLIENT, caching_key, 
                            app.config.CACHING_TTL['LEVEL_EIGHT'])

    if not cache_valid:
        data = await eth_contract_details(app, request_args)
        await set_cache(app.config.REDIS_CLIENT, caching_key, data)
        return data
    result= await get_cache(app.config.REDIS_CLIENT, caching_key)
    return json.loads(result)



def make_query_string(request_args: dict, args_list: list) -> str:
    query_string = ""
    for (key, value) in request_args.items():
        if key in args_list:
            if type(value) == list:
                value = value[0]
            query_string += f"&{key}={value}"
    return query_string[1:] # to 


async def contract_text_caching(app: object, caching_key: str, request_args: dict) -> any: 
    cache_valid = await cache_validity(app.config.REDIS_CLIENT, caching_key, 
                            app.config.CACHING_TTL['LEVEL_SEVEN'])

    if not cache_valid:
        data = await eth_contract_on_text(request_args.get("text"))
        await set_cache(app.config.REDIS_CLIENT, caching_key, data)
        return data
    result= await get_cache(app.config.REDIS_CLIENT, caching_key)
    return json.loads(result)

@TOKEN_SEARCH_BP.get('<chain>/text')
#@authorized
async def search_text(request, chain):
    if chain not in request.app.config.SUPPORTED_CHAINS:
        raise CustomError("chain not suported")
    request.args["chain"] = chain
    if  not request.args.get("text"):
        raise CustomError("text is required")

    query_string: str = make_query_string(request.args, ["text"])
    caching_key = f"{request.route.path}?{query_string}"

    erc_standard = await contract_text_caching(request.app, caching_key, request.args)

    result = eth_contract_on_text(request.args.get("text"))
    return Response.success_response(data=result)



@TOKEN_SEARCH_BP.get('<chain>/contract_type')
# @is_subscribed()
async def get_contract_type(request, chain):
    if  chain not in request.app.config.SUPPORTED_CHAINS:
        raise CustomError("chain not suported")

    if  not request.args.get("contract_address"):
        raise CustomError("contract_address is required")

    query_string: str = make_query_string(request.args, ["contract_address"])
    caching_key = f"erc_standard?{query_string}"
    logger.info(f"Here is the caching key {caching_key}")
    erc_standard = await contract_standard_type_caching(request.app, caching_key, request.args)
    return Response.success_response(data=erc_standard)
