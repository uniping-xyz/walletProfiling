
import requests
import json
import asyncio
import aiohttp
from sanic import Blueprint
from utils.utils import Response
from utils.errors import CustomError
from loguru import logger

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

    logger.success(f"Length of the result returned is {len(result)}")
    return Response.success_response(data=result)