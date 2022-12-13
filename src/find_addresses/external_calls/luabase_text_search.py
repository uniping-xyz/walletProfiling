
import os
import aiohttp

async def search_erc20_text(session,  text):
    url = "https://q.luabase.com/run"

    payload = {
    "block": {
        "data_uuid": "c263e31ce99a4681a2b8ca347d4a4b3f",
        "details": {
            "limit": 10,
            "parameters": {
            "home": {
                    "type": "value",
                    "value": ""
                },
                "query": {
                    "type": "value",
                    "value": text
            }
                        }
        }
    },
     "api_key": os.environ['LUABASE_API_KEY']
    }
    headers = {"content-type": "application/json"}
    # async with session.post(url, json={'test': 'object'})
    # response = requests.request("POST", url, json=payload, headers=headers)
    
    async with session.post(url, json=payload, headers=headers) as response:
        data =  await response.json()
    return data["data"]

async def search_erc721_text(session, text):
    url = "https://q.luabase.com/run"

    payload = {
    "block": {
        "data_uuid": "638504aeccd84f89ac509ec1161872f1",
        "details": {
            "limit": 10,
            "parameters": {
            "home": {
                    "type": "value",
                    "value": ""
                },
                "query": {
                    "type": "value",
                    "value": text
            }
                        }
        }
    },
     "api_key": os.environ['LUABASE_API_KEY']

    }
    headers = {"content-type": "application/json"}
    async with session.post(url, json=payload, headers=headers) as response:
        data =  await response.json()

    return data["data"]

async def search_erc1155_text(session, text):
    url = "https://q.luabase.com/run"

    payload = {
    "block": {
        "data_uuid": "7568715f03a546a085ff57316bdc0d44",
        "details": {
            "limit": 10,
            "parameters": {
            "home": {
                    "type": "value",
                    "value": ""
                },
                "query": {
                    "type": "value",
                    "value": text
            }
                        }
        }
    },
     "api_key": os.environ['LUABASE_API_KEY']
    }
    headers = {"content-type": "application/json"}

    async with session.post(url, json=payload, headers=headers) as response:
        data =  await response.json()

    return data["data"]
