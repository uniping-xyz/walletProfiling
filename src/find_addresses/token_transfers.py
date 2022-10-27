
import requests
import json
import asyncio
import aiohttp
from sanic import Blueprint
from utils.utils import Response
from utils.errors import CustomError
from loguru import logger


TOKEN_TRANSFERS_BP = Blueprint("transfers", url_prefix='/transfers', version=1)


"""
WITH genesis AS (
  SELECT *
  FROM
    ethereum.contracts
  WHERE
    address = LOWER('{{contract_address}}')
  LIMIT 1)

select from, to, token_id, type, standard, transfer_type, transfer_unique_id, block_timestamp, transaction_hash
from ethereum.nft_transfers as t 
where DATE(block_timestamp)  >= DATE((SELECT block_timestamp FROM genesis))
order by block_timestamp desc
limit {{limit}}
offset {{offset}}

"""
async def erc721_1155_transfers(session, luabase_api_key, contract_address, limit, offset):
    url = "https://q.luabase.com/run"

    payload = {
        "block": {
            "data_uuid": "4c4fa5f6fe484f9fb4adade404fae893",
            "details": {
                "limit": 2000,
                "parameters": {
                    "contract_address": {
                        "value": contract_address.lower(),
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
    # async with session.post(url, json={'test': 'object'})
    # response = requests.request("POST", url, json=payload, headers=headers)
    
    async with session.post(url, json=payload, headers=headers) as response:
        data =  await response.json()
    return data["data"]

"""
WITH genesis AS (
  SELECT *
  FROM
    ethereum.contracts
  WHERE
    address = LOWER('{{contract_address}}')
  LIMIT 1)

select block_timestamp, transaction_hash, token_address, from_address, to_address, value
from ethereum.token_transfers as t 
where DATE(block_timestamp)  >= DATE((SELECT block_timestamp FROM genesis))
order by block_timestamp desc
limit {{limit}}
offset {{offset}}

"""
async def erc20_transfers(session, luabase_api_key, contract_address, limit, offset):
    url = "https://q.luabase.com/run"

    payload = {
        "block": {
            "data_uuid": "4e120e31a0584683a4042df14d2629df",
            "details": {
                "limit": 2000,
                "parameters": {
                    "contract_address": {
                        "value": contract_address.lower(),
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
    # async with session.post(url, json={'test': 'object'})
    # response = requests.request("POST", url, json=payload, headers=headers)
    
    async with session.post(url, json=payload, headers=headers) as response:
        data =  await response.json()
    return data["data"]


@TOKEN_TRANSFERS_BP.get('token_transfers')
#@authorized
async def token_transfers(request):
    if request.args.get("chain") not in request.app.config.SUPPORTED_CHAINS:
        raise CustomError("chain not suported")

    if not request.args.get("standard"):
        raise CustomError("standard is required")

    if not request.args.get("standard") in ['erc721', 'erc20', 'erc1155']:
        raise CustomError("not a valid standard ")

    if not request.args.get("contract_address"):
        raise CustomError("contract_address is required")

    if not request.args.get("standard"):
        raise CustomError("standard is required")

    if not request.args.get("limit"):
        limit = 25
    else:
        limit = request.args.get("limit")

    if not request.args.get("offset"):
        offset = 0
    else:
        offset = request.args.get("offset")


    async with aiohttp.ClientSession() as session:
        if  not request.args.get("standard") in ['erc721', 'erc1155']:

            response = await erc721_1155_transfers(session, request.app.config.LUABASE_API_KEY, 
                    request.args.get("contract_address"), limit, offset)
        else:
            response = await erc20_transfers(session, request.app.config.LUABASE_API_KEY, 
                    request.args.get("contract_address"), limit, offset)

    return Response.success_response(data=response)