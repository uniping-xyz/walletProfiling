


import requests
import os
import aiohttp
from eth_utils import to_checksum_address


async def wallet_txs_per_day(wallet_address, number_of_days):

    url = "https://q.luabase.com/run"

    payload = {
    "block": {
        "data_uuid": os.environ["WALLET_STATS_TRANSACTIONS_PER_DAY_DATA_UUID"],
        "details": {
            "limit": 2000,
            "parameters": {
                "days": {
                    "type": "value",
                    "value": str(number_of_days)
                },
                "wallet_address": {
                    "type": "value",
                    "value": wallet_address
                }
            }
        }
    },
        "api_key": os.environ["WALLET_STATS_LUABASE_API_KEY"],
    }
    headers = {"content-type": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            data =  await response.json()
    return data["data"]


async def wallet_txs(wallet_address, number_of_days):

    url = "https://q.luabase.com/run"

    payload = {
    "block": {
        "data_uuid": os.environ["WALLET_STATS_TRANSACTIONS_DATA_UUID"],
        "details": {
            "limit": 2000,
            "parameters": {
                "days": {
                    "type": "value",
                    "value": str(number_of_days)
                },
                "wallet_address": {
                    "type": "value",
                    "value": wallet_address
                }
            }
        }
        },
        "api_key": os.environ["WALLET_STATS_LUABASE_API_KEY"],
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
        "data_uuid": os.environ["WALLET_STATS_OUTGOING_TABLE_DATA_UUID"],
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
        "api_key": os.environ["WALLET_STATS_LUABASE_API_KEY"],
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
            "data_uuid": os.environ["WALLET_STATS_INCOMING_TABLE_DATA_UUID"],
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
        "api_key": os.environ["WALLET_STATS_LUABASE_API_KEY"],
    }
    headers = {"content-type": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            data =  await response.json()
    return data["data"]