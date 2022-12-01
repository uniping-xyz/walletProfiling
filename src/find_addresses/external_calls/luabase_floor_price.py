import aiohttp
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
async def floor_price_per_day(contract_address, number_of_days):
    url = "https://q.luabase.com/run"

    payload = {
        "block": {
            "data_uuid": "eb99579b3e5a4fcab10fae1667a32196",
            "details": {
                "limit": 2000,
                "parameters": {
                    "days": {
                        "value": str(number_of_days),
                        "type": "value"
                    },
                    "contract_address": {
                        "type": "value",
                        "value": contract_address
                    }
                }
            }
        },
        "api_key": os.environ['LUABASE_API_KEY'],
    }

    headers = {"content-type": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            data =  await response.json()
    return data["data"]