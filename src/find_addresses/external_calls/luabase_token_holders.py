

import os
import aiohttp

async def holders_ERC20(contract_address, limit, offset):
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
        "api_key": os.environ["LUABASE_API_KEY"],
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
        "api_key": os.environ["LUABASE_API_KEY"],
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
            "data_uuid": "184517a47f5546a2b0f86ef91104e1db",
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
        "api_key": os.environ["LUABASE_API_KEY"],
    }
    headers = {"content-type": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            data  = await resp.json()
    return data["data"]
