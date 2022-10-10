

import requests
import json



async def get_ethereum_tags(lubabase_api_key):
    url = "https://q.luabase.com/run"

    payload = {
    "block": {
        "data_uuid": "958a4cdf11684438942e591e9bdb6e18"
    },
    "api_key": lubabase_api_key,
    "parameters": {
        "label": {
            "value": "defi",
            "type": "value"
        }
    }
    }
    headers = {"content-type": "application/json"}
    response = requests.request("POST", url, json=payload, headers=headers)
    data = response.json() 
    return data["data"]



async def get_tagged_ethereum_contracts(lubabase_api_key, tag):

    url = "https://q.luabase.com/run"

    payload = {
    "block": {
        "data_uuid": "99310c5e8af9418197027ba9c8af3e24"
    },
    "api_key": lubabase_api_key,
    "parameters": {
        "label": {
            "value": tag,
            "type": "value"
        }
    }
    }
    headers = {"content-type": "application/json"}
    response = requests.request("POST", url, json=payload, headers=headers)
    data = response.json()
    return data["data"]
