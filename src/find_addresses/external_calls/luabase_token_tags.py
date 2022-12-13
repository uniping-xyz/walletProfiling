
import aiohttp
import os

async def get_ethereum_tags(label):
    url = "https://q.luabase.com/run"

    
    payload = {
    "block": {
        "data_uuid":  os.environ['TAGS_DATA_UUID'],
        "details": {
            "limit": 2000,
            "parameters": {
                "query": {
                    "value": "defi",
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



async def get_tagged_ethereum_contracts(tag):
    url = "https://q.luabase.com/run"


    payload = {
    "block": {
        "data_uuid": os.environ['TAGS_DATA_UUID'],
        "details": {
            "limit": 2000,
            "parameters": {
                "query": {
                    "value": "defi",
                    "type": "value"
                }
            }
        }
    },
        "api_key": os.environ['TAGS_CONTRACTS_DATA_UUID'],
    }
    headers = {"content-type": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            data  = await resp.json()
    return data["data"]
