
import aiohttp
import os
async def topERC20( chain, limit, offset, number_of_days):
    url = "https://q.luabase.com/run"
    payload = {
        "block": {
            "data_uuid": os.environ["TRENDING_ERC20_DATA_UUID"],
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
        "api_key": os.environ["TRENDING_LUABASE_API_KEY"],
    }
    headers = {"content-type": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            data  = await resp.json() 
    print (data)
    return data["data"]

async def topERC1155(chain, limit, offset, number_of_days):
    STANDARD = 'erc1155'
    url = "https://q.luabase.com/run"

    payload = {
        "block": {
            "data_uuid": os.environ["TRENDING_ERC721_DATA_UUID"],
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
        "api_key": os.environ["TRENDING_LUABASE_API_KEY"],
    }

    headers = {"content-type": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            data  = await resp.json()
    return data["data"]

async def topERC721(chain, limit, offset, number_of_days):
    STANDARD = 'erc721'
    url = "https://q.luabase.com/run"

    payload = {
        "block": {
            "data_uuid": os.environ["TRENDING_ERC721_DATA_UUID"],
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
        "api_key": os.environ["TRENDING_LUABASE_API_KEY"],
    }

    headers = {"content-type": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            data  = await resp.json()
    return data["data"]