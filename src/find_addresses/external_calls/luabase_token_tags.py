
import aiohttp
import os

async def get_ethereum_tags():
    url = "https://q.luabase.com/run"

    payload = {
    "block": {
        "data_uuid": "958a4cdf11684438942e591e9bdb6e18"
    },
        "api_key": os.environ["LUABASE_API_KEY"],
    "parameters": {
        "label": {
            "value": "defi",
            "type": "value"
        }
    }
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
        "data_uuid": "99310c5e8af9418197027ba9c8af3e24",
        "details": {
            "parameters": {
                "label": {
                    "value": tag,
                    "type": "value"
                }
            }
        }
    },
        "api_key": os.environ["LUABASE_API_KEY"],
    }
    headers = {"content-type": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            data  = await resp.json()
    return data["data"]
