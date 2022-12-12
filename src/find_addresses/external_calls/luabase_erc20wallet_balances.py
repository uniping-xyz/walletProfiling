

import requests
import os
import aiohttp
from eth_utils import to_checksum_address


async def eth_erc20_wallet_balance(wallet_address):

    url = "https://q.luabase.com/run"

    payload = {
        "block": {
            "data_uuid": "23a5fa6682fd425ba6fb90f9f9441ef8",
            "details": {
                "limit": 2000,
                "parameters": {}
            }
        },
        "api_key": os.environ["LUABASE_API_KEY"],
    }
    headers = {"content-type": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            data =  await response.json()
    
    return data.get("data")
