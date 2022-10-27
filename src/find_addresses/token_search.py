
import requests
import json
import asyncio
import aiohttp
from sanic import Blueprint
from utils.utils import Response
from utils.errors import CustomError
from loguru import logger
from .token_holders import holders_ERC1155, holders_ERC20, holders_ERC721

TOKEN_SEARCH_BP = Blueprint("search", url_prefix='/search/tokens', version=1)



async def search_erc20_text(session, luabase_api_key, text):
    url = "https://q.luabase.com/run"

    payload = {
    "block": {
        "data_uuid": "c263e31ce99a4681a2b8ca347d4a4b3f",
        "details": {
            "parameters": {
            "home": {
                    "type": "value",
                    "value": ""
                },
                "query": {
                    "type": "value",
                    "value": text
            }
                        }
        }
    },
     "api_key": luabase_api_key
    }
    headers = {"content-type": "application/json"}
    # async with session.post(url, json={'test': 'object'})
    # response = requests.request("POST", url, json=payload, headers=headers)
    
    async with session.post(url, json=payload, headers=headers) as response:
        data =  await response.json()
    return data["data"]

async def search_erc721_text(session, luabase_api_key, text):
    url = "https://q.luabase.com/run"

    payload = {
    "block": {
        "data_uuid": "638504aeccd84f89ac509ec1161872f1",
        "details": {
            "parameters": {
            "home": {
                    "type": "value",
                    "value": ""
                },
                "query": {
                    "type": "value",
                    "value": text
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

async def search_erc1155_text(session, luabase_api_key, text):
    url = "https://q.luabase.com/run"

    payload = {
    "block": {
        "data_uuid": "7568715f03a546a085ff57316bdc0d44",
        "details": {
            "parameters": {
            "home": {
                    "type": "value",
                    "value": ""
                },
                "query": {
                    "type": "value",
                    "value": text
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



"""
select is_erc20, is_erc721, is_erc1155, function_sighashes, block_timestamp 
from ethereum.contracts  
where address == lower('{{token_address}}')
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


"""
select standard
from ethereum.nft_transfers  
where contract_address == lower('{{token_address}}')
limit 1
"""
async def search_contract_nft_transfers(session, luabase_api_key, contract_address):
    url = "https://q.luabase.com/run"

    payload = {
        "block": {
            "data_uuid": "09d7e7740ddf4b368cdf84abd8d1626d",
            "details": {
                "limit": 2000,
                "parameters": {
                    "token_address": {
                        "type": "value",
                        "value": contract_address.lower()
                    }
                }
            }
        },
        "api_key": luabase_api_key,
    }
    
    headers = {"content-type": "application/json"}

    async with session.post(url, json=payload, headers=headers) as response:
        data =  await response.json()

    return data["data"]



"""
select *
from ethereum.token_transfers  
where token_address == lower('{{token_address}}')
"""
async def search_contract_erc20_transfers(session, luabase_api_key, contract_address):
    url = "https://q.luabase.com/run"

    payload = {
        "block": {
            "data_uuid": "54ca20e088a94c8090bbd6316135d547",
            "details": {
                "limit": 2000,
                "parameters": {
                    "token_address": {
                        "type": "value",
                        "value": contract_address.lower()
                    }
                }
            }
        },
        "api_key": luabase_api_key,
    }
        
    headers = {"content-type": "application/json"}

    async with session.post(url, json=payload, headers=headers) as response:
        data =  await response.json()

    return data["data"]



async def find_standard_if_proxy(luabase_api_key, contract_address):
    async with aiohttp.ClientSession() as session:
        new_response = await search_contract_nft_transfers(session,luabase_api_key, contract_address)

    if new_response:
        logger.success("Proxied ERC721 or ERC1155 contract found")
        return new_response[0].get('standard')
    
    async with aiohttp.ClientSession() as session:
        new_response = await search_contract_erc20_transfers(session,luabase_api_key, contract_address)

    if new_response:
        logger.success("Proxied ERC20 contract found")

        return 'erc20'
    
    return None



async def get_holders(standard, luabase_api_key, contract_address):
    logger.info('Fetching holders')
    if standard == 'erc721':
        return await holders_ERC721(luabase_api_key, 
            contract_address, 100, 0)
    elif standard == 'erc1155':
        return await holders_ERC1155(luabase_api_key, 
            contract_address, 100, 0)
    elif standard == 'erc20':
        return await holders_ERC20(luabase_api_key, 
            contract_address, 100, 0)
    
    else:
        return []

    return 

"""
Based on the contract address, this API gives you the standard of the contract address
even if that contract address is a proxy
Also gives the the top holders of the token
"""
@TOKEN_SEARCH_BP.get('search_contract_address')
#@authorized
async def search_contract_address(request):
    if  request.args.get("chain") not in request.app.config.SUPPORTED_CHAINS:
        raise CustomError("chain not suported")

    if  not request.args.get("contract_address"):
        raise CustomError("contract_address is required")

    async with aiohttp.ClientSession() as session:
        _response = await search_contract_contracts_table(session, request.app.config.LUABASE_API_KEY, 
                    request.args.get("contract_address"))
    
    logger.info(_response)
    if not _response:
        raise CustomError("No contract found")

    response = _response[0]
    result = {}

    if response.get("is_erc20"):
        logger.success("ERC20 contract found")
        result['standard'] = 'erc20'
        result['holders']  = await holders_ERC20(request.app.config.LUABASE_API_KEY, 
            request.args.get("contract_address"), 100, 0)

    elif response.get("is_erc721"):
        logger.success("ERC721 contract found")
        result['standard'] = 'erc721'
    
   
    elif response.get("is_erc1155"):
        logger.success("ERC1155 contract found")
        result['standard'] = 'erc1155'

    else:
        logger.success("Probabaly a Proxy contract found")
        _response = await find_standard_if_proxy(request.app.config.LUABASE_API_KEY, 
                    request.args.get("contract_address"))
        result['standard'] = _response

    result['holders']  = await get_holders(result['standard'], 
                                    request.app.config.LUABASE_API_KEY, 
                                request.args.get("contract_address"))    

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
                search_erc20_text(session, request.app.config.LUABASE_API_KEY, request.args.get("text")),
                search_erc721_text(session, request.app.config.LUABASE_API_KEY, request.args.get("text")), 
                search_erc1155_text(session, request.app.config.LUABASE_API_KEY, request.args.get("text"))],                
                return_exceptions=True)

    logger.success(result)
    logger.success(f"Length of the result returned is {len(result)}")
    return Response.success_response(data=result)