import requests
import json
import asyncio
import aiohttp
from sanic import Blueprint
from utils.utils import Response
from utils.errors import CustomError
from loguru import logger

TOKEN_HOLDERS_BP = Blueprint("holders", url_prefix='/holders/', version=1)



async def holders_ERC20(luabase_api_key, contract_address, limit, offset):
    url = "https://q.luabase.com/run"
    payload = {
        "block": {
            "data_uuid": "83a97a46ae29491eb285ea1cbf2f58dc",
            "details": {
                "limit": 2000,
                "parameters": {
                    "contract_address": {
                        "type": "value",
                        "value": contract_address.lower()
                    },
                    "limit": {
                        "type": "value",
                        "value": str(limit)
                    },
                    "offset": {
                        "type": "value",
                        "value": str(offset)
                    }
                }
            }
        },
        "api_key": luabase_api_key,
    }
    headers = {"content-type": "application/json"}
    response = requests.request("POST", url, json=payload, headers=headers)
    data = response.json() 
    print (data)
    return data["data"]

async def holders_ERC1155(luabase_api_key, contract_address, limit, offset):
    url = "https://q.luabase.com/run"

    payload = {
        "block": {
            "data_uuid": "db64bc5123024e069472dde52417c849",
            "details": {
                "limit": 2000,
                "parameters": {
                    "limit": {
                        "type": "value",
                        "value": str(limit)
                    },
                    "offset": {
                        "type": "value",
                        "value": str(offset)
                    },
                    "contract_address": {
                        "type": "value",
                        "value": contract_address.lower()
                    }
                }
            }
        },
        "api_key": luabase_api_key,
    }

    headers = {"content-type": "application/json"}
    response = requests.request("POST", url, json=payload, headers=headers)
    data = response.json()
    print (data)
    return data["data"]

async def holders_ERC721(luabase_api_key, contract_address, limit, offset):
    url = "https://q.luabase.com/run"

    payload = {
    "block": {
        "data_uuid": "608865f109864114a75ad41f222e0ee3",
        "details": {
            "limit": 2000,
            "parameters": {
                "limit": {
                    "type": "value",
                    "value": str(limit)
                },
                "offset": {
                    "type": "value",
                    "value": str(offset)
                },
                "contract_address": {
                    "type": "value",
                    "value": contract_address.lower()
                }
            }
        }
    },
    "api_key": luabase_api_key,
    }

    headers = {"content-type": "application/json"}
    response = requests.request("POST", url, json=payload, headers=headers)
    data = response.json()
    print (data)
    return data["data"]


@TOKEN_HOLDERS_BP.get('tokens')
#@authorized
async def token_holders(request):
    if request.args.get("chain") not in request.app.config.SUPPORTED_CHAINS:
        raise CustomError("chain not suported")

    if not request.args.get("erc_type"):
        raise CustomError("ERC Type is required")

    if not request.args.get("contract_address"):
        raise CustomError("contract_address is required")

    if not request.args.get("erc_type") in ["ERC20", "ERC721", "ERC1155"]:
        raise CustomError("ERC Type is not valid")

    if not request.args.get("limit"):
        limit = 20
    else:
        limit = request.args.get("limit")


    if not request.args.get("offset"):
        offset = 0
    else:
        offset = request.args.get("offset")


    if request.args.get("erc_type") ==  "ERC20":
        results = await holders_ERC20(request.app.config.LUABASE_API_KEY,  
                    request.args.get("contract_address"), limit, offset)

    elif request.args.get("erc_type") ==  "ERC721":
        results = await holders_ERC721(request.app.config.LUABASE_API_KEY,  
                    request.args.get("contract_address"), limit, offset)    
    else:
        results = await holders_ERC1155(request.app.config.LUABASE_API_KEY,  
                    request.args.get("contract_address"), limit, offset)
    result = []
    for row in results:
        result.append({
                "balance": row['balance'],
                "address": row['address'],
        })    
    logger.success(result)
    logger.success(f"Length of the result returned is {len(result)}")
    return Response.success_response(data=result)
