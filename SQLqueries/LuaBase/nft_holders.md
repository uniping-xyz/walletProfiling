-- select * 
-- from ethereum.erc721_transfers 
-- where contract_address = lower('0x3Df5c619a4926156f966A64E08f863385C21Da0e')
-- ORDER by block_timestamp DESC

WITH genesis AS (
  SELECT *
  FROM
    ethereum.contracts
  WHERE
    address = LOWER('{{contract_address}}')),

added_row_number AS(
  SELECT *,
    ROW_NUMBER() OVER(PARTITION BY token_id ORDER BY block_timestamp DESC) AS row_number
  FROM
     ethereum.erc721_transfers
  WHERE
    DATE(block_timestamp)  >= DATE((
      SELECT
        block_timestamp
      FROM
        genesis))
    AND contract_address = LOWER('{{contract_address}}') ),

token_ownership AS (
  SELECT
    token_id,
    to
  FROM
    added_row_number
  WHERE
    row_number = 1
  ORDER BY
    token_id DESC ),

result as (
SELECT
  COUNT(1) AS count,
  to
FROM
  token_ownership
GROUP BY
  to
ORDER BY
  count DESC
LIMIT 100 )

select * from result
```


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
      "contract_address": {
            "value": "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D",
            "type": "value"
      }
}
  }
}
headers = {"content-type": "application/json"}
response = requests.request("POST", url, json=payload, headers=headers)
data = response.json() 
```