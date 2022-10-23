### ERC721 token holders : table_name {{home}}.erc721_token_owners

#### QUery sql on luabase
```
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
        AND type = 'send'

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
        AND type = 'send'

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
```
#### luabase API
```
LUABASE_API_KEY = os.getenv('LUABASE_API_KEY')

url = "https://q.luabase.com/run"

payload = {
    "block": {
        "data_uuid": "608865f109864114a75ad41f222e0ee3",
        "details": {
            "limit": 2000,
            "parameters": {
                "limit": {
                    "type": "value",
                    "value": "5"
                },
                "offset": {
                    "type": "value",
                    "value": "0"
                },
                "contract_address": {
                    "type": "value",
                    "value": "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D"
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

###ERC20 holders 

```
WITH genesis AS (
  SELECT *
  FROM
    ethereum.contracts
  WHERE
    address = LOWER('{{contract_address}}')
  LIMIT 1),

wallet_balances AS (
      SELECT
        toFloat64(value) AS value,
        block_timestamp,
        to_address AS address
      FROM
        ethereum.token_transfers
      WHERE
        DATE(block_timestamp)  >= DATE((SELECT block_timestamp FROM genesis))
        AND token_address =  LOWER('{{contract_address}}')
        AND to_address is not null

      UNION ALL
      SELECT
        -toFloat64(value) AS value,
        block_timestamp,
        from_address AS address
      FROM
       ethereum.token_transfers
      WHERE
        DATE(block_timestamp)  >= DATE((SELECT block_timestamp FROM genesis))
        AND token_address =  LOWER('{{contract_address}}')
        AND from_address is not null 

),

aggregated_wallet_balances AS (
   SELECT
      address,
      round(SUM(value)/pow(10, 18), 4) AS balance
  from wallet_balances
  group by  address
)

select * from aggregated_wallet_balances
order by balance desc
limit {{limit}}
offset {{offset}}
```
#### Luabase API 
```

LUABASE_API_KEY = os.getenv('LUABASE_API_KEY')

url = "https://q.luabase.com/run"

payload = {
    "block": {
        "data_uuid": "83a97a46ae29491eb285ea1cbf2f58dc",
        "details": {
            "limit": 2000,
            "parameters": {
                "contract_address": {
                    "type": "value",
                    "value": "0x3506424F91fD33084466F402d5D97f05F8e3b4AF"
                },
                "limit": {
                    "type": "value",
                    "value": "10"
                },
                "offset": {
                    "type": "value",
                    "value": "0"
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

