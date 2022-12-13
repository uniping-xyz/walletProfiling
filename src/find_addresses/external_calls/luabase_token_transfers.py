
import aiohttp
import os
"""
WITH genesis AS (
  SELECT *
  FROM
    ethereum.contracts
  WHERE
    address = LOWER('{{contract_address}}')
  LIMIT 1)

select from, to, block_timestamp, contract_address, token_id, quantity, transfer_type, type
from ethereum.nft_transfers as t 
where DATE(block_timestamp)  >= DATE((SELECT block_timestamp FROM genesis))
and contract_address = LOWER('{{contract_address}}')
order by block_timestamp desc
limit {{limit}}
offset {{offset}}
"""
async def search_contract_nft_transfers(contract_address, limit, offset):
    url = "https://q.luabase.com/run"

    payload = {
        "block": {
            "data_uuid":os.environ['ETH_NFT_TRANSFERS_DATA_UUID'],
            "details": {
                "limit": 2000,
                "parameters": {
                    "contract_address": {
                        "type": "value",
                        "value": contract_address
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
        "api_key":  os.environ['ETH_TOKEN_TRANSFERS_LUABASE_API_KEY'],
    }
    headers = {"content-type": "application/json"}


    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            data =  await response.json()
    return data["data"]



"""
select *
from ethereum.token_transfers  
where token_address == lower('{{token_address}}')
"""
async def search_contract_erc20_transfers(contract_address, limit, offset):
    url = "https://q.luabase.com/run"

    payload = {
        "block": {
            "data_uuid": os.environ['ETH_ERC20_TRANSFERS_DATA_UUID'],
            "details": {
                "limit": 2000,
                "parameters": {
                    "limit": {
                        "type": "value",
                        "value": limit
                    },
                    "offset": {
                        "type": "value",
                        "value": offset
                    },
                    "contract_address": {
                        "type": "value",
                        "value": contract_address
                    }
                }
            }
        },
        "api_key":  os.environ['ETH_TOKEN_TRANSFERS_LUABASE_API_KEY'],
    }
    headers = {"content-type": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            data =  await response.json()
    return data["data"]