
### Query
#### Live view name: top_erc20_contracts

```with total_transactions_pertoken_perday as(
  select count(*) as total_transactions,
  contract_address
  from ethereum.erc20_transfers
  WHERE 
    DATE(block_timestamp) > DATE(now()) - toIntervalDay('{{number_of_days}}')
  GROUP by
    contract_address
  ORDER BY total_transactions DESC
),

with_names as (
  select tt.total_transactions, tt.contract_address, pp.address, pp.name, pp.symbol from total_transactions_pertoken_perday as tt
  left join
  ethereum.amended_tokens as pp
  on lower(tt.contract_address) = lower(pp.address)
)
select * from with_names
```

#### Python request

```
import requests
import os

LUABASE_API_KEY = os.getenv('LUABASE_API_KEY')

url = "https://q.luabase.com/run"

payload = {
  "block": {
    "data_uuid": "8a3a96a16a354abe84dfb089155f5b18"
  },
  "api_key": LUABASE_API_KEY,
  "details": {
    "parameters": {
      "chain": {
            "type": "value",
            "value": "ethereum"
      },
      "number_of_days": {
            "type": "value",
            "value": "3"
      }
}
  }
}
headers = {"content-type": "application/json"}
response = requests.request("POST", url, json=payload, headers=headers)
data = response.json() 



```