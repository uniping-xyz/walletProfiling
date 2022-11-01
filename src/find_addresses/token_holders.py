import requests
import json
import asyncio
import aiohttp
from sanic import Blueprint
from utils.utils import Response
from utils.errors import CustomError
from loguru import logger
from sanic.request import RequestParameters
from caching.cache_utils import cache_validity, get_cache, set_cache, delete_cache

TOKEN_HOLDERS_BP = Blueprint("holders", url_prefix='/holders/', version=1)

"""
WITH genesis AS (
  SELECT *
  FROM
    ethereum.contracts
  WHERE
    address = LOWER('{{contract_address}}')
  LIMIT 1),

wallet_balances AS (
      SELECT
        toInt64(1) AS value,
        block_timestamp,
        to AS address
      FROM
        ethereum.nft_transfers
      WHERE
        standard = 'erc1155'
        AND DATE(block_timestamp)  >= DATE((SELECT block_timestamp FROM genesis))
        AND contract_address =  LOWER('{{contract_address}}')
        AND to is not null

      UNION ALL
      SELECT
        -toInt64(1) AS value,
        block_timestamp,
        from AS address
      FROM
       ethereum.nft_transfers
      WHERE
        standard = 'erc1155'
        AND DATE(block_timestamp)  >= DATE((SELECT block_timestamp FROM genesis))
        AND contract_address =  LOWER('{{contract_address}}')
        AND from is not null
),

aggregated_wallet_balances AS (
   SELECT
      address,
      SUM(value) AS balance
  from wallet_balances
  group by  address
)

select * from aggregated_wallet_balances
order by balance desc
limit {{limit}}
offset {{offset}}
"""

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
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            data  = await resp.json()

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
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            data  = await resp.json()


    # headers = {"content-type": "application/json"}
    # response = requests.request("POST", url, json=payload, headers=headers)
    # data = response.json()
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
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            data  = await resp.json()


    # headers = {"content-type": "application/json"}
    # response = requests.request("POST", url, json=payload, headers=headers)
    # data = response.json()
    print (data)
    return data["data"]


def make_query_string(request_args: dict) -> str:
    query_string = ""
    for (key, value) in request_args.items():
        if type(value) == list:
            value = value[0]
        query_string += f"&{key}={value}"
    return query_string[1:] # to remove the first $ sign appened to the string

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
        request.args["limit"] = [20]

    if not request.args.get("offset"):
        request.args["offset"] = [0]

    query_string: str = make_query_string(request.args)

    if request.app.config.CACHING:
        caching_key = f"{request.route.path}?{query_string}"
        logger.info(f"Here is the caching key {caching_key}")
        data = await token_holders_caching(request.app, caching_key, request.args)
    else:
        data = await fetch_data(request.app, request.args)
    
    result = []
    for row in data:
        result.append({
                "balance": row['balance'],
                "address": row['address'],
        })

    logger.success(f"Length of the result returned is {len(result)}")
    return Response.success_response(data=result)


async def token_holders_caching(app: object, caching_key: str, request_args: dict) -> any: 
    cache_valid = await cache_validity(app.config.REDIS_CLIENT, caching_key, 
                            app.config.CACHING_TTL['LEVEL_FIVE'])

    if not cache_valid:
        data = await fetch_data(app, request_args)
        await set_cache(app.config.REDIS_CLIENT, caching_key, data)
        return data
    result= await get_cache(app.config.REDIS_CLIENT, caching_key)
    return json.loads(result)

async def fetch_data(app: object, request_args: RequestParameters) -> any:

    if request_args.get("erc_type") ==  "ERC20":
        results = await holders_ERC20(app.config.LUABASE_API_KEY,  
                    request_args.get("contract_address"),  request_args.get("limit"),  
                    request_args.get("offset"))

    elif request_args.get("erc_type") ==  "ERC721":
        results = await holders_ERC721(app.config.LUABASE_API_KEY,  
                    request_args.get("contract_address"),  request_args.get("limit"),  
                    request_args.get("offset"))    
    else:
        results = await holders_ERC1155(app.config.LUABASE_API_KEY,  
                    request_args.get("contract_address"),  request_args.get("limit"),  
                    request_args.get("offset"))
    return results