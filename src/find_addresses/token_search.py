
from xml.dom.minidom import Document
import requests
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
from .token_holders import holders_ERC1155, holders_ERC20, holders_ERC721
from caching.cache_utils import cache_validity, get_cache, set_cache
from data.populate_blockdaemon import  check_blockDaemon_tokens_staleness, \
            populate_erc721_blockdaemon, populate_erc1155_blockdaemon
from data.populate_coingecko import check_coingecko_tokens_staleness, fetch_coingecko_token_list
from find_addresses.external_calls import luabase_text_search 


from find_addresses.db_calls.erc20.ethereum import search_contract_address as erc20_eth_search
from find_addresses.db_calls.erc721.ethereum import search_contract_address as erc721_eth_search
from find_addresses.db_calls.erc1155.ethereum import search_contract_address as erc1155_eth_search

TOKEN_SEARCH_BP = Blueprint("search", url_prefix='/search/tokens', version=1)




async def find_standard_if_proxy(session, luabase_api_key, contract_address):
    new_response = await search_contract_nft_transfers(session, luabase_api_key, contract_address)

    if new_response:
        logger.success("Proxied ERC721 or ERC1155 contract found")
        return new_response[0].get('standard')
    
    async with aiohttp.ClientSession() as session:
        new_response = await search_contract_erc20_transfers(session,luabase_api_key, contract_address)

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


"""
select is_erc20, is_erc721, is_erc1155, function_sighashes, block_timestamp 
from ethereum.contracts  
where address == lower('{{token_address}}')

Sample response:
[{'is_erc20': 1, 'is_erc721': 0, 'is_erc1155': 0, 
'function_sighashes': ['0x06fdde03', '0x095ea7b3', '0x18160ddd', '0x23b872dd', 
'0x2e1a7d4d', '0x313ce567', '0x70a08231', '0x95d89b41', '0xa9059cbb', '0xd0e30db0', 
'0xdd62ed3e', '_fallback()'], 'block_timestamp': '2017-12-12T11:17:35'}]
"""
async def search_contract_contracts_table(session, luabase_api_key, contract_address):
    url = "https://q.luabase.com/run"


    payload = {
        "block": {
            "data_uuid": "6996ac2efa374930bf46dfe8ebfa7bc3",
            "details": {
                "limit": 2000,
                "parameters": {
                    "token_address": {
                        "value": contract_address.lower(),
                        "type": "value"
                    }
                }
            }
        },
     "api_key": luabase_api_key
    }
    
    headers = {"content-type": "application/json"}

    async with session.post(url, json=payload, headers=headers) as response:
        data =  await response.json()
    return data["data"]




# provides the standard of the contract address
async def fetch_contract_standard_type(app: object, request_args: dict):
    async with aiohttp.ClientSession() as session:
        response = await search_contract_contracts_table(session, 
                app.config.LUABASE_API_KEY, 
                request_args.get("contract_address"))
        if not response:
            logger.error(f'{request_args.get("contract_address")} ERC_STANDARD=[{None }]')
            return None   
        for (key, standard) in [("is_erc20", "erc20"), ("is_erc721", "erc721"), ("is_erc1155", "erc1155")]:
            if response[0].get(key):
                logger.success(f'{request_args.get("contract_address")} ERC_STANDARD=[{standard}]')
                return standard
        logger.warning("Probabaly a Proxy contract found")

        _response = await find_standard_if_proxy(session, 
                            app.config.LUABASE_API_KEY, 
                            request_args.get("contract_address"))
        logger.success(f'{request_args.get("contract_address")} ERC_STANDARD=[{_response }]')
        if _response:
            return _response
        logger.error(f'{request_args.get("contract_address")} ERC_STANDARD=[{None }]')
        return None



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
        print ("ERC20 found")
        results = await holders_ERC20(app.config.LUABASE_API_KEY,  
                    request_args.get("contract_address"), 100, 0)

    elif request_args.get("erc_type") ==  "erc721":
        print ("ERC721 found")
        results = await holders_ERC721(app.config.LUABASE_API_KEY,  
                    request_args.get("contract_address"), 100, 0)    
    else:
        print (f"ERC1155 found ")
        results = await holders_ERC1155(app.config.LUABASE_API_KEY,  
                    request_args.get("contract_address"), 100, 0)
    return results












@TOKEN_SEARCH_BP.get('new/text')
#@authorized
async def search_text(request):
    await check_coingecko_tokens_staleness(request.app)
    await check_blockDaemon_tokens_staleness(request.app) ##
    if  request.args.get("chain") not in request.app.config.SUPPORTED_CHAINS:
        raise CustomError("chain not suported")

    if  not request.args.get("text"):
        raise CustomError("search Text is required")
    await check_blockDaemon_tokens_staleness(request.app) ##this checks if the coingecko token list in db is not older than 5 hours

    logger.info("Fetching results from mongodb")
    result = await asyncio.gather(*[
                search_erc20_text(request.app, request.args.get("text")),
                search_erc721_text(request.app, request.args.get("text")),
                search_erc1155_text(request.app, request.args.get("text")), 
                 ],                
                return_exceptions=True)

    logger.success(result)
    logger.success(f"Length of the result returned is {len(result)}")
    data = {
        "erc20": result[0],
        "erc721": result[1],
        "erc1155": result[2]
    }
    return Response.success_response(data=data)





async def contract_standard_type_caching(app: object, caching_key: str, request_args: dict) -> any: 
    cache_valid = await cache_validity(app.config.REDIS_CLIENT, caching_key, 
                            app.config.CACHING_TTL['LEVEL_ZERO'])

    if not cache_valid:
        data = await seach_contract_address_in_db(app, request_args)
        await set_cache(app.config.REDIS_CLIENT, caching_key, data)
        return data
    result= await get_cache(app.config.REDIS_CLIENT, caching_key)
    return json.loads(result)

async def seach_contract_address_in_db(app: object, request_args) -> any: 
    logger.info("Ethered in to search contractaddress in db")
    result = None
    result = await search_erc20_contract_address(app, request_args.get("contract_address"))
    if not result:
        result = await search_erc721_contract_address(app, request_args.get("contract_address"))
    if not result:
        result = await search_erc1155_contract_address(app, request_args.get("contract_address"))

    if result.get("contracts"):
        if type(result.get("contracts")) == list:
            contracts = result.pop("contracts")
            result.update({"contracts": contracts})
    return result

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




@TOKEN_SEARCH_BP.get('text')
#@authorized
async def search_text(request):
    if  request.args.get("chain") not in request.app.config.SUPPORTED_CHAINS:
        raise CustomError("chain not suported")

    if  not request.args.get("text"):
        raise CustomError("search Text is required")

    async with aiohttp.ClientSession() as session:
        result = await asyncio.gather(*[
                luabase_text_search.search_erc20_text(session, request.app.config.LUABASE_API_KEY, request.args.get("text")),
                luabase_text_search.search_erc721_text(session, request.app.config.LUABASE_API_KEY, request.args.get("text")), 
                luabase_text_search.search_erc1155_text(session, request.app.config.LUABASE_API_KEY, request.args.get("text"))],                
                return_exceptions=True)

    logger.success(result)
    logger.success(f"Length of the result returned is {len(result)}")
    return Response.success_response(data=result)




@TOKEN_SEARCH_BP.get('populate_tokens')
async def populate_tokens(request):
    # request.app.add_task(populate_erc721_blockdaemon(request.app))
    # request.app.add_task(populate_erc1155_blockdaemon(request.app))
    request.app.add_task(fetch_coingecko_token_list(request.app))
    return Response.success_response(data={})
