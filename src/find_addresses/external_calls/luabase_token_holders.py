

import os
import aiohttp

async def holders_ERC20(contract_address, limit, offset):
    url = "https://q.luabase.com/run"
    payload = {
        "block": {
            "data_uuid": os.environ['ETH_HOLDERS_ERC20_DATA_UUID'],
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
        "api_key":  os.environ['ETH_HOLDERS_LUABASE_API_KEY'],
    }

    headers = {"content-type": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            data  = await resp.json()
    return data["data"]

async def holders_ERC1155(contract_address, limit, offset):
    url = "https://q.luabase.com/run"

    payload = {
        "block": {
            "data_uuid": os.environ['ETH_HOLDERS_ERC721_DATA_UUID'],
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
        "api_key":  os.environ['ETH_HOLDERS_LUABASE_API_KEY'],
    }
    headers = {"content-type": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            data  = await resp.json()

    return data["data"]

async def holders_ERC721( contract_address, limit, offset):
    url = "https://q.luabase.com/run"

    payload = {
        "block": {
            "data_uuid": os.environ['ETH_HOLDERS_1155_DATA_UUID'],
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
        "api_key":  os.environ['ETH_HOLDERS_LUABASE_API_KEY'],
    }
    headers = {"content-type": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            data  = await resp.json()
    return data["data"]
