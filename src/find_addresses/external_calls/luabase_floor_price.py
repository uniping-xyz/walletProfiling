




import requests
import os

"""
WITH genesis AS (
  SELECT *
  FROM
    ethereum.contracts
  WHERE
    address = LOWER('{{contract_address}}')
  LIMIT 1),

filtered_transactions as (
    select
        block_number,
        block_timestamp,
        block_hash,
        hash as transaction_hash,
        value_eth,
        transaction_fee_eth
    from ethereum.transactions
    where  block_timestamp >= date(date_sub(day, 90, now()))
    and hash in (
select transaction_hash
        from ethereum.token_transfers
        where  block_timestamp >= date(date_sub(day, 90, now())) 
        and token_address = LOWER('{{contract_address}}') 
)
)

select DATE(block_timestamp) as _date , sum(value_eth) as floor_price
from filtered_transactions 
group by _date
"""
async def find_floor_price(session, luabase_api_key, contract_address):
    url = "https://q.luabase.com/run"
    LUABASE_API_KEY = os.getenv('LUABASE_API_KEY')

    url = "https://q.luabase.com/run"

    payload = {
        "block": {
            "data_uuid": "eb99579b3e5a4fcab10fae1667a32196",
            "details": {
                "limit": 2000,
                "parameters": {
                    "contract_address": {
                        "type": "value",
                        "value": contract_address
                    }
                }
            }
        },
        "api_key": LUABASE_API_KEY,
    }
    headers = {"content-type": "application/json"}
    response = requests.request("POST", url, json=payload, headers=headers)
    data = response.json() 