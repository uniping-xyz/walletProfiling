
"""
select standard
from ethereum.nft_transfers  
where contract_address == lower('{{token_address}}')
limit 1
"""
async def search_contract_nft_transfers(session, luabase_api_key, contract_address):
    url = "https://q.luabase.com/run"

    payload = {
        "block": {
            "data_uuid": "09d7e7740ddf4b368cdf84abd8d1626d",
            "details": {
                "limit": 2000,
                "parameters": {
                    "token_address": {
                        "type": "value",
                        "value": contract_address.lower()
                    }
                }
            }
        },
        "api_key": luabase_api_key,
    }
    
    headers = {"content-type": "application/json"}

    async with session.post(url, json=payload, headers=headers) as response:
        data =  await response.json()

    return data["data"]



"""
select *
from ethereum.token_transfers  
where token_address == lower('{{token_address}}')
"""
async def search_contract_erc20_transfers(session, luabase_api_key, contract_address):
    url = "https://q.luabase.com/run"

    payload = {
        "block": {
            "data_uuid": "54ca20e088a94c8090bbd6316135d547",
            "details": {
                "limit": 2000,
                "parameters": {
                    "token_address": {
                        "type": "value",
                        "value": contract_address.lower()
                    }
                }
            }
        },
        "api_key": luabase_api_key,
    }

    headers = {"content-type": "application/json"}
    async with session.post(url, json=payload, headers=headers) as response:
        data =  await response.json()

    return data["data"]