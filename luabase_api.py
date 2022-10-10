

import requests
import os
import pprint

LUABASE_API_KEY = os.getenv('LUABASE_API_KEY')

url = "https://q.luabase.com/run"



def get_tags():
    payload = {
    "block": {
        "data_uuid": "f8e0e465ffdb4f10a33ee8d3dc9389f0"
    },
    "api_key": LUABASE_API_KEY,
    "parameters": {}
    }
    headers = {"content-type": "application/json"}
    response = requests.request("POST", url, json=payload, headers=headers)
    data = response.json()
    pprint.pprint(data)


    