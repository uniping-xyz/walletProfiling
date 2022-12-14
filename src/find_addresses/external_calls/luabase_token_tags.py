
import aiohttp
import os

async def eth_all_tags():
    url = "https://q.luabase.com/run"

    payload = {
    "block": {
        "data_uuid":  os.environ['TAGS_ALL_DATA_UUID'],
        "details": {
            "limit": 2000,
            "parameters": {
            }
        }
    },
    "api_key": os.environ['TAGS_LUABASE_API_KEY'],
    }
    headers = {"content-type": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            data  = await resp.json()
    return data["data"]

async def get_tagged_ethereum_contracts(tag):
    url = "https://q.luabase.com/run"


    payload = {
    "block": {
        "data_uuid": os.environ['TAGS_CONTRACTS_DATA_UUID'],
        "details": {
            "limit": 2000,
            "parameters": {
                "query": {
                    "value": tag,
                    "type": "value"
                }
            }
        }
    },
        "api_key": os.environ['TAGS_LUABASE_API_KEY'],
    }
    headers = {"content-type": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            data  = await resp.json()
    return data["data"]


"""
select distinct label, Count(*) as contracts
from ethereum.tags
group by label
order by contracts desc
"""
async def get_all_ethereum_tags_with_contracts():
    url = "https://q.luabase.com/run"

    payload = {
        "block": {
            "data_uuid": os.environ['TAGS_ALL_WITH_CONTRACTS_DATA_UUID'],
            "details": {
                "limit": 2000,
                "parameters": {}
            }
        },
            "api_key": os.environ['TAGS_LUABASE_API_KEY'],
    }
    headers = {"content-type": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            data  = await resp.json()

    return data.get("data")
