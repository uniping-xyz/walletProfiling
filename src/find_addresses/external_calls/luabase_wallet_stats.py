


import requests
import os
import aiohttp
from eth_utils import to_checksum_address


async def wallet_txs_per_day(wallet_address):

    url = "https://q.luabase.com/run"

    payload = {
        "block": {
            "data_uuid": "55696395705b484ba8ce29c50c6ad4d7",
            "details": {
                "limit": 2000,
                "parameters": {
                    "wallet_address": {
                        "value": to_checksum_address(wallet_address),
                        "type": "value"
                    }
                }
            }
        },
        "api_key": os.environ["LUABASE_API_KEY"],
    }
    headers = {"content-type": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            data =  await response.json()
    return data["data"]


async def wallet_txs(wallet_address):

    url = "https://q.luabase.com/run"

    payload = {
        "block": {
            "data_uuid": "fcde6f7adee3496ebb31bd12053c9c18",
            "details": {
                "limit": 2000,
                "parameters": {
                    "wallet_address": {
                        "value": to_checksum_address(wallet_address),
                        "type": "value"
                    }
                }
            }
        },
        "api_key": os.environ["LUABASE_API_KEY"],
    }
    headers = {"content-type": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            data =  await response.json()
    return data["data"]


async def wallet_most_outgoing_interactions(wallet_address, number_of_days):


    url = "https://q.luabase.com/run"

    payload = {
    "block": {
        "data_uuid": "fa480213f1354ddbae42b039b05685a7",
        "details": {
            "limit": 2000,
            "parameters": {
                "wallet_address": {
                    "value": wallet_address,
                    "type": "value"
                },
                "days": {
                    "value": str(number_of_days),
                    "type": "value"
                }
            }
        }
        },
        "api_key": os.environ["LUABASE_API_KEY"],
    }
    headers = {"content-type": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            data =  await response.json()
    return data["data"]

async def wallet_most_incoming_interactions(wallet_address, number_of_days):
    url = "https://q.luabase.com/run"


    payload = {
        "block": {
            "data_uuid": "f36f6323dd714456812060c3dcf298eb",
            "details": {
                "limit": 2000,
                "parameters": {
                    "wallet_address": {
                        "value": "0x9c5083dd4838E120Dbeac44C052179692Aa5dAC5",
                        "type": "value"
                    },
                    "days": {
                        "value": "180",
                        "type": "value"
                    }
                }
            }
        },
        "api_key": os.environ["LUABASE_API_KEY"],
    }
    headers = {"content-type": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            data =  await response.json()
    return data["data"]