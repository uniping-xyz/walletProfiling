
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
from find_addresses.external_calls import luabase_token_holders
from caching.cache_utils import cache_validity, get_cache, set_cache
from populate_data.populate_blockdaemon import  check_blockDaemon_tokens_staleness, \
            populate_erc721_blockdaemon, populate_erc1155_blockdaemon
from populate_data.populate_coingecko import check_coingecko_tokens_staleness, fetch_coingecko_token_list
from find_addresses.external_calls import luabase_text_search 
from find_addresses.external_calls import luabase_contract_search

from find_addresses.db_calls.erc20.ethereum import search_contract_address as erc20_eth_search
from find_addresses.db_calls.erc721.ethereum import search_contract_address as erc721_eth_search
from find_addresses.db_calls.erc1155.ethereum import search_contract_address as erc1155_eth_search

TOKEN_SEARCH_BP = Blueprint("search", url_prefix='/search/tokens', version=1)

"""
Based on the contract address, this API gives you the standard of the contract address
even if that contract address is a proxy
Also gives the the top holders of the token
"""
@TOKEN_SEARCH_BP.get('search_contract_address')
@is_subscribed()
async def search_contract_address(request):
    if  request.args.get("chain") not in request.app.config.SUPPORTED_CHAINS:
        raise CustomError("chain not suported")

    if  not request.args.get("contract_address"):
        raise CustomError("contract_address is required")

    query_string: str = make_query_string(request.args, ["chain", "contract_address"])
    if request.app.config.CACHING:
            caching_key = f"erc_standard?{query_string}"
            logger.info(f"Here is the caching key {caching_key}")
            erc_standard = await contract_standard_type_caching(request.app, caching_key, request.args)
    else:
        erc_standard = await fetch_contract_standard_type(request.app, request.args)

    result = {}

    if erc_standard:
        request.args["erc_type"] = [erc_standard]
        result['standard'] = erc_standard
        print (request.args)
        if request.app.config.CACHING:
                caching_key = f"token_holders_for_{erc_standard}?{query_string}"
                logger.info(f"Here is the caching key {caching_key}")
                result['holders'] = await token_holders_caching(request.app, caching_key, request.args)
        else:
            result['holders'] = await fetch_token_holders(request.app, request.args)
    return Response.success_response(data=result)

async def contract_standard_type_caching(app: object, caching_key: str, request_args: dict) -> any: 
    cache_valid = await cache_validity(app.config.REDIS_CLIENT, caching_key, 
                            app.config.CACHING_TTL['LEVEL_ZERO'])

    if not cache_valid:
        data = await fetch_contract_standard_type(app, request_args)
        await set_cache(app.config.REDIS_CLIENT, caching_key, data)
        return data
    result= await get_cache(app.config.REDIS_CLIENT, caching_key)
    return json.loads(result)


async def fetch_contract_standard_type(app: object, request_args: dict):
    response = await luabase_contract_search.search_contract_contracts_table(request_args.get("contract_address"))
    if not response:
        logger.error(f'{request_args.get("contract_address")} ERC_STANDARD=[{None }]')
        return None   
    for (key, standard) in [("is_erc20", "erc20"), ("is_erc721", "erc721"), ("is_erc1155", "erc1155")]:
        if response[0].get(key):
            logger.success(f'{request_args.get("contract_address")} ERC_STANDARD=[{standard}]')
            return standard
    logger.warning("Probabaly a Proxy contract found")

    _response = await find_standard_if_proxy(request_args.get("contract_address"))
    logger.success(f'{request_args.get("contract_address")} ERC_STANDARD=[{_response }]')
    if _response:
        return _response
    logger.error(f'{request_args.get("contract_address")} ERC_STANDARD=[{None }]')
    return None


async def find_standard_if_proxy(contract_address):
    new_response = await luabase_contract_search.search_contract_nft_transfers(contract_address)

    if new_response:
        logger.success("Proxied ERC721 or ERC1155 contract found")
        return new_response[0].get('standard')
    
    new_response = await luabase_contract_search.search_contract_erc20_transfers(contract_address)

    if new_response:
        logger.success("Proxied ERC20 contract found")
        return 'erc20'
    
    return None


def make_query_string(request_args: dict, args_list: list) -> str:
    query_string = ""
    for (key, value) in request_args.items():
        if key in args_list:
            if type(value) == list:
                value = value[0]
            query_string += f"&{key}={value}"
    return query_string[1:] # to 



async def token_holders_caching(app: object, caching_key: str, request_args: dict) -> any: 
    cache_valid = await cache_validity(app.config.REDIS_CLIENT, caching_key, 
                            app.config.CACHING_TTL['LEVEL_FIVE'])

    if not cache_valid:
        data = await fetch_token_holders(app, request_args)
        await set_cache(app.config.REDIS_CLIENT, caching_key, data)
        return data
    result= await get_cache(app.config.REDIS_CLIENT, caching_key)
    return json.loads(result)

async def fetch_token_holders(app: object, request_args: dict) -> any:

    if request_args.get("erc_type") ==  "erc20":
        results = await luabase_token_holders.holders_ERC20( 
                    request_args.get("contract_address"), 100, 0)

    elif request_args.get("erc_type") ==  "erc721":
        results = await luabase_token_holders.holders_ERC721(  
                    request_args.get("contract_address"), 100, 0)    
    else:
        results = await luabase_token_holders.holders_ERC1155(  
                    request_args.get("contract_address"), 100, 0)
    return results


@TOKEN_SEARCH_BP.get('text')
#@authorized
async def search_text(request):
    if  request.args.get("chain") not in request.app.config.SUPPORTED_CHAINS:
        raise CustomError("chain not suported")

    if  not request.args.get("text"):
        raise CustomError("search Text is required")

    async with aiohttp.ClientSession() as session:
        result = await asyncio.gather(*[
                luabase_text_search.search_erc20_text(session, request.args.get("text")),
                luabase_text_search.search_erc721_text(session, request.args.get("text")), 
                luabase_text_search.search_erc1155_text(session,request.args.get("text"))],                
                return_exceptions=True)

    return Response.success_response(data=result)




@TOKEN_SEARCH_BP.get('populate_tokens')
async def populate_tokens(request):
    request.app.add_task(populate_erc721_blockdaemon(request.app))
    request.app.add_task(populate_erc1155_blockdaemon(request.app))
    request.app.add_task(fetch_coingecko_token_list(request.app))
    return Response.success_response(data={})
