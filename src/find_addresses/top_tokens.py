import requests
import json
import asyncio
import aiohttp
from sanic import Blueprint
from utils.utils import Response
from utils.errors import CustomError
from loguru import logger

MOST_POPULAR_BP = Blueprint("most_popular", url_prefix='/most_popular/tokens', version=1)



async def topERC20(luabase_api_key, chain, limit, offset, number_of_days):
    url = "https://q.luabase.com/run"
    payload = {
        "block": {
            "data_uuid": "3a67d1de7cf9449d864813cc129f9e97",
            "details": {
                "limit": 2000,
                "parameters": {
                    "chain": {
                        "value": chain,
                        "type": "value"
                    },
                    "number_of_days": {
                        "value": number_of_days,
                        "type": "value"
                    },
                    "limit": {
                        "value": limit,
                        "type": "value"
                    },
                    "offset": {
                        "value": offset,
                        "type": "value"
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

async def topERC1155(luabase_api_key, chain, limit, offset, number_of_days):
    STANDARD = 'erc1155'
    url = "https://q.luabase.com/run"

    payload = {
        "block": {
            "data_uuid": "3d9e2c5ca87c4a50a8c6908fdd5b316f",
            "details": {
                "limit": 2000,
                "parameters": {
                    "chain": {
                        "type": "value",
                        "value": chain
                    },
                    "number_of_days": {
                        "type": "value",
                        "value": number_of_days
                    },
                    "standard": {
                        "value": STANDARD,
                        "type": "value"
                    },
                    "limit": {
                        "type": "value",
                        "value": limit
                    },
                    "offset": {
                        "type": "value",
                        "value": offset
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

async def topERC721(luabase_api_key, chain, limit, offset, number_of_days):
    STANDARD = 'erc721'
    url = "https://q.luabase.com/run"

    payload = {
        "block": {
            "data_uuid": "3d9e2c5ca87c4a50a8c6908fdd5b316f",
            "details": {
                "limit": 2000,
                "parameters": {
                    "chain": {
                        "type": "value",
                        "value": chain
                    },
                    "number_of_days": {
                        "type": "value",
                        "value": number_of_days
                    },
                    "standard": {
                        "value": STANDARD,
                        "type": "value"
                    },
                    "limit": {
                        "type": "value",
                        "value": limit
                    },
                    "offset": {
                        "type": "value",
                        "value": offset
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


@MOST_POPULAR_BP.get('most_popular')
#@authorized
async def most_popular(request):
    if request.args.get("chain") not in request.app.config.SUPPORTED_CHAINS:
        raise CustomError("chain not suported")

    if not request.args.get("erc_type"):
        raise CustomError("ERC Type is required")

    if not request.args.get("erc_type") in ["ERC20", "ERC721", "ERC1155"]:
        raise CustomError("ERC Type is not valid")

    if not request.args.get("number_of_days"):
        number_of_days = 3
    else:
        number_of_days = request.args.get("number_of_days")


    if not request.args.get("limit"):
        limit = 20
    else:
        limit = request.args.get("limit")


    if not request.args.get("offset"):
        offset = 0
    else:
        offset = request.args.get("offset")


    if request.args.get("erc_type") ==  "ERC20":
        results = await topERC20(request.app.config.LUABASE_API_KEY,  
                    request.args.get("chain"), limit, offset, number_of_days)

    elif request.args.get("erc_type") ==  "ERC721":
        results = await topERC721(request.app.config.LUABASE_API_KEY,  
                    request.args.get("chain"), limit, offset, number_of_days)    
    else:
        results = await topERC1155(request.app.config.LUABASE_API_KEY,  
                    request.args.get("chain"), limit, offset, number_of_days)
    result = []
    for row in results:
        result.append({
                "total_transactions": row['total_transactions'],
                "contract_address": row['contract_address'],
                "name": row['name'],
                "symbol": row['symbol']
        })    
    logger.success(result)
    logger.success(f"Length of the result returned is {len(result)}")
    return Response.success_response(data=result)
