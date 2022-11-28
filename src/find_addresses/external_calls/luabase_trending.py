
import aiohttp

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