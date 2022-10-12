## Creates three different lists that does have name, symbol and contract_type


### ERC1155, {{home}}.erc1155token_names 

```
select DISTINCT contract_address, 'erc1155' as contract_type, t.name, t.symbol
from ethereum.erc1155_transfers_single
INNER JOIN
ethereum.amended_tokens as t
ON
contract_address == t.address
```


#### Python code

```
import requests
import os

LUABASE_API_KEY = os.getenv('LUABASE_API_KEY')

url = "https://q.luabase.com/run"

payload = {
  "block": {
    "data_uuid": "f835d83ad48843a5861b5bb083360a5b"
  },
  "api_key": LUABASE_API_KEY,
  "details": {
    "parameters": {}
  }
}
headers = {"content-type": "application/json"}
response = requests.request("POST", url, json=payload, headers=headers)
data = response.json() 
```

### ERC721, {{home}}.erc721token_names 

```
select DISTINCT contract_address, 'erc721' as contract_type, t.name, t.symbol
from ethereum.erc721_transfers
INNER JOIN
ethereum.amended_tokens as t
ON
contract_address == t.address
```


#### Python code

```
import requests
import os

LUABASE_API_KEY = os.getenv('LUABASE_API_KEY')

url = "https://q.luabase.com/run"

payload = {
  "block": {
    "data_uuid": "3be6321ff9c2431ab29c0c85469df432"
  },
  "api_key": LUABASE_API_KEY,
  "details": {
    "parameters": {}
  }
}
headers = {"content-type": "application/json"}
response = requests.request("POST", url, json=payload, headers=headers)
data = response.json() 


```

### ERC20, {{home}}.erc20token_names 

```
select DISTINCT contract_address, 'erc20' as contract_type, t.name, t.symbol
from ethereum.erc20_transfers
INNER JOIN
ethereum.amended_tokens as t
ON
contract_address == t.address
```


#### Python code

```
import requests
import os

LUABASE_API_KEY = os.getenv('LUABASE_API_KEY')

url = "https://q.luabase.com/run"

payload = {
  "block": {
    "data_uuid": "3be6321ff9c2431ab29c0c85469df432"
  },
  "api_key": LUABASE_API_KEY,
  "details": {
    "parameters": {}
  }
}
headers = {"content-type": "application/json"}
response = requests.request("POST", url, json=payload, headers=headers)
data = response.json() 


```


## FIND the name or symbol

```
with erc721 as (select * from {{home}}.erc20token_names
WHERE name LIKE '{{query}}%'
and symbol LIKE '{{query}}%'),

erc20 as (
select * from {{home}}.erc721token_names 
WHERE name LIKE '{{query}}%'
and symbol LIKE '{{query}}%'
),

erc1155 as (
select * from {{home}}.erc1155token_names 
WHERE name LIKE '{{query}}%'
and symbol LIKE '{{query}}%'
)

select * from erc20
FULL JOIN 
erc721
on 
    erc20.contract_address = erc721.contract_address
FULL JOIN
erc1155
on 
 erc20.contract_address = erc1155.contract_address
 ```