

import requests
import json
import pprint



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



async def get_tagged_ethereum_contracts(luabase_api_key, tag):
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
    "api_key": luabase_api_key
    }
    headers = {"content-type": "application/json"}
    response = requests.request("POST", url, json=payload, headers=headers)
    data = response.json()
    return data["data"]




def topERC20(luabase_api_key, chain, number_of_days):
    url = "https://q.luabase.com/run"

    payload = {
      "block": {
        "data_uuid": "aebb592047534769b0002cd880a35b5a",
        "details": {
            "parameters": {
                 "chain": {
                     "type": "value",
                     "value": chain
                      },
                  "number_of_days": {
                        "type": "value",
                        "value": number_of_days
                          }
                    }
                  }
            },
        "api_key": luabase_api_key
        }
    headers = {"content-type": "application/json"}
    response = requests.request("POST", url, json=payload, headers=headers)
    data = response.json()
    print (data)
    return data["data"]

def topERC1155(luabase_api_key, chain, number_of_days):
    url = "https://q.luabase.com/run"

    payload = {
      "block": {
        "data_uuid": "f835d83ad48843a5861b5bb083360a5b",
        "details": {
            "parameters": {
                 "chain": {
                     "type": "value",
                     "value": chain
                      },
                  "number_of_days": {
                        "type": "value",
                        "value": number_of_days
                          }
                    }
                  }
            },
        "api_key": luabase_api_key
        }
    headers = {"content-type": "application/json"}
    response = requests.request("POST", url, json=payload, headers=headers)
    data = response.json()
    print (data)
    return data["data"]

def topERC721(luabase_api_key, chain, number_of_days):
    url = "https://q.luabase.com/run"

    payload = {
      "block": {
        "data_uuid": "3be6321ff9c2431ab29c0c85469df432",
        "details": {
            "parameters": {
                 "chain": {
                     "type": "value",
                     "value": chain
                      },
                  "number_of_days": {
                        "type": "value",
                        "value": number_of_days
                          }
                    }
                  }
            },
        "api_key": luabase_api_key
        }
    headers = {"content-type": "application/json"}
    response = requests.request("POST", url, json=payload, headers=headers)
    data = response.json()
    print (data)
    return data["data"]



