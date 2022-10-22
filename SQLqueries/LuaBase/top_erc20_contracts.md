
### Query
#### Live view name: top_erc20_contracts

```
with total_transactions_pertoken_perday as(
  select count(*) as total_transactions,
  token_address
  from {{chain}}.token_transfers
  WHERE 
    DATE(block_timestamp) > DATE(now()) - toIntervalDay('{{number_of_days}}')
    AND  token_address NOT IN (SELECT DISTINCT contract_address FROM {{chain}}.nft_transfers)
  GROUP by
    token_address
  ORDER BY total_transactions DESC 
),

with_names as (
  select distinct tt.total_transactions, tt.token_address, pp.address, pp.name, pp.symbol from total_transactions_pertoken_perday as tt
  left join
  ethereum.tokens as pp
  on lower(tt.token_address) = lower(pp.address)
)
select * from with_names 
LIMIT {{limit}}
OFFSET {{offset}}

```

#### Python request

```
Python
import requests
import os

LUABASE_API_KEY = os.getenv('LUABASE_API_KEY')

url = "https://q.luabase.com/run"

payload = {
    "block": {
        "data_uuid": "3a67d1de7cf9449d864813cc129f9e97",
        "details": {
            "limit": 2000,
            "parameters": {
                "chain": {
                    "value": "ethereum",
                    "type": "value"
                },
                "number_of_days": {
                    "value": "7",
                    "type": "value"
                },
                "limit": {
                    "value": "20",
                    "type": "value"
                },
                "offset": {
                    "value": "0",
                    "type": "value"
                }
            }
        }
    },
    "api_key": LUABASE_API_KEY,
}
headers = {"content-type": "application/json"}
response = requests.request("POST", url, json=payload, headers=headers)
data = response.json()
```