with total_transactions_pertoken_perday as(
  select count(*) as total_transactions,
  contract_address
  from ethereum.erc1155_transfers_single
  -- where DATE(block_timestamp) BETWEEN '{{from_data}}' and '{{to_date}}'
  WHERE 
    DATE(block_timestamp) > DATE(now()) - toIntervalDay(3)
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


#### LIVE VIEW

```
import requests
import os

LUABASE_API_KEY = os.getenv('LUABASE_API_KEY')

url = "https://q.luabase.com/run"

payload = {
  "block": {
    "data_uuid": "3d9e2c5ca87c4a50a8c6908fdd5b316f"
  },
  "api_key": LUABASE_API_KEY,
  "details": {
    "parameters": {
      "number_of_days": {
            "value": "3",
            "type": "value"
      }
}
  }
}
headers = {"content-type": "application/json"}
response = requests.request("POST", url, json=payload, headers=headers)
data = response.json() 


```