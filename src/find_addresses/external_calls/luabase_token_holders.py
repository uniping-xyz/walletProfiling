

import os
import aiohttp

async def holders_ERC20(contract_address, limit, offset):
    url = "https://q.luabase.com/run"
    payload = {
        "block": {
            "data_uuid": os.environ['ETH_HOLDERS_ERC20_DATA_UUID'],
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
        "api_key":  os.environ['ETH_HOLDERS_LUABASE_API_KEY'],
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
            "data_uuid": os.environ['ETH_HOLDERS_ERC1155_DATA_UUID'],
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
        "api_key":  os.environ['ETH_HOLDERS_LUABASE_API_KEY'],
    }
    headers = {"content-type": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            data  = await resp.json()

    return data["data"]

async def holders_ERC721( contract_address, limit, offset):
    sql = '''
                WITH genesis AS (
        SELECT *
        FROM
            ethereum.contracts
        WHERE
            address = LOWER('{{contract_address}}')
        LIMIT 1),

        wallet_balances AS (
            SELECT
                toInt64(1) AS value,
                block_timestamp,
                to AS address
            FROM
                ethereum.nft_transfers
            WHERE
                standard = 'erc721'
                AND DATE(block_timestamp)  >= DATE((SELECT block_timestamp FROM genesis))
                AND contract_address =  LOWER('{{contract_address}}')
                AND to is not null

            UNION ALL
            SELECT
                -toInt64(1) AS value,
                block_timestamp,
                from AS address
            FROM
            ethereum.nft_transfers
            WHERE
                standard = 'erc721'
                AND DATE(block_timestamp)  >= DATE((SELECT block_timestamp FROM genesis))
                AND contract_address =  LOWER('{{contract_address}}')
                AND from is not null
        ),

        aggregated_wallet_balances AS (
        SELECT
            address,
            SUM(value) AS balance
        from wallet_balances
        group by  address
        )

        select * from aggregated_wallet_balances
        order by balance desc
        limit {{limit}}
        offset {{offset}}
    
    '''


    url = "https://q.luabase.com/run"

    payload = {
        "block": {
            "data_uuid": os.environ['ETH_HOLDERS_ERC721_DATA_UUID'],
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
        "api_key":  os.environ['ETH_HOLDERS_LUABASE_API_KEY'],
    }
    headers = {"content-type": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            data  = await resp.json()
    return data["data"]
