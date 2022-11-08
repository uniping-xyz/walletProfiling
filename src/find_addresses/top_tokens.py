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
from caching.cache_utils import cache_validity, get_cache, set_cache, delete_cache

MOST_POPULAR_BP = Blueprint("most_popular", url_prefix='/most_popular/tokens', version=1)

"""
This is the live view  {{home}}.all_time_erc20_live_view and it runs daily

with total_transactions_pertoken_perday as(
  select count(*) as total_transactions,
  token_address
  from {{chain}}.token_transfers
  WHERE 
    token_address NOT IN (SELECT DISTINCT contract_address FROM {{chain}}.nft_transfers)
  GROUP by
    token_address
  ORDER BY total_transactions DESC 
),

with_names as (
  select distinct tt.total_transactions, tt.token_address as contract_address, pp.address, pp.name, pp.symbol from total_transactions_pertoken_perday as tt
  left join
  ethereum.tokens as pp
  on lower(tt.token_address) = lower(pp.address)
)
select * from with_names
The query that fetches contracts from this live view is this
"""

async def all_time_top_erc20(luabase_api_key, chain, limit, offset, number_of_days):
    url = "https://q.luabase.com/run"
    payload = {
        "block": {
            "data_uuid": "86ab5185ea0f479785e36bfd5da05797",
            "details": {
                "limit": 2000,
                "parameters": {
                    "chain": {
                        "type": "value",
                        "value": chain
                    },
                    "number_of_days": {
                        "type": "value",
                        "value": "7"
                    },
                    "limit": {
                        "type": "value",
                        "value": "20"
                    },
                    "offset": {
                        "type": "value",
                        "value": "0"
                    }
                }
            }
        },
        "api_key": luabase_api_key,
    }
    headers = {"content-type": "application/json"}
    response = requests.request("POST", url, json=payload, headers=headers)
    data = response.json() 
    return data["data"]


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
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            data  = await resp.json() 
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
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            data  = await resp.json()
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
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            data  = await resp.json()
    return data["data"]

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
                            app.config.CACHING_TTL['LEVEL_FIVE'])

    if not cache_valid:
        data = await fetch_data(app, request_args)
        await set_cache(app.config.REDIS_CLIENT, caching_key, data)
        return data
    result= await get_cache(app.config.REDIS_CLIENT, caching_key)
    return json.loads(result)

async def fetch_data(app: object, request_args: RequestParameters) -> any:
    if request_args.get("erc_type") ==  "ERC20":
        logger.info("ERC20 token_type")
        results = await topERC20(app.config.LUABASE_API_KEY,  
                        request_args.get("chain"), request_args.get("limit"), 
                        request_args.get("offset"), request_args.get("number_of_days"))

    elif request_args.get("erc_type") ==  "ERC721":
        logger.info("ERC721 token_type")
        results = await topERC721(app.config.LUABASE_API_KEY,  
                        request_args.get("chain"), request_args.get("limit"), 
                        request_args.get("offset"), request_args.get("number_of_days"))   
    else:
        logger.info("ERC1155 token_type")
        results = await topERC1155(app.config.LUABASE_API_KEY,  
                        request_args.get("chain"), request_args.get("limit"), 
                        request_args.get("offset"), request_args.get("number_of_days"))
    return results