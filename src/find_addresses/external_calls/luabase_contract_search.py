
import os
import aiohttp

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
async def search_contract_contracts_table(contract_address):
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
        "api_key": os.environ["LUABASE_API_KEY"],
    }
    
    headers = {"content-type": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            data =  await response.json()
    return data["data"]





async def search_contract_nft_transfers(contract_address):
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
        "api_key": os.environ["LUABASE_API_KEY"],
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
async def search_contract_erc20_transfers(contract_address):
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
        "api_key": os.environ["LUABASE_API_KEY"],
    }

    headers = {"content-type": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            data =  await response.json()

    return data["data"]