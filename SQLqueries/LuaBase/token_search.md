
### Token search on erc20, erc721, and erc1155 types.


#### Search token on erc20 types. {{home}}.erc20token_search
```
select contract_address, contract_type, name, symbol 
from {{home}}.erc20token_names
WHERE lower_name LIKE '{{query}}%'
and lower_symbol LIKE '{{query}}%'
```

```
LUABASE_API_KEY = os.getenv('LUABASE_API_KEY')

url = "https://q.luabase.com/run"

payload = {
  "block": {
    "details": {
        "parameters": {
        "home": {
                "type": "value",
                "value": ""
        },
        "query": {
                "type": "value",
                "value": "gh"
        }
        }
    },
    "api_key": LUABASE_API_KEY,
  
}
headers = {"content-type": "application/json"}
response = requests.request("POST", url, json=payload, headers=headers)
data = response.json()
```



#### Search token name on erc721  {{home}}.erc721token_search
```
select contract_address, contract_type, name, symbol 
from {{home}}.erc721token_names
WHERE lower_name LIKE '{{query}}%'
and lower_symbol LIKE '{{query}}%'
```

```
url = "https://q.luabase.com/run"

payload = {
  "block": {
    "data_uuid": "638504aeccd84f89ac509ec1161872f1"
  },
  "api_key": LUABASE_API_KEY,
  "details": {
    "parameters": {
      "home": {
            "type": "value",
            "value": ""
      },
      "query": {
            "type": "value",
            "value": "gh"
      }
}
  }
}
headers = {"content-type": "application/json"}
response = requests.request("POST", url, json=payload, headers=headers)
data = response.json() 
```

#### Search token name on erc1155  {{home}}.erc1155token_search

```
select contract_address, contract_type, name, symbol 
from {{home}}.erc1155token_names
WHERE lower_name LIKE '{{query}}%'
or lower_symbol LIKE '{{query}}%'
```

```
url = "https://q.luabase.com/run"

payload = {
  "block": {
    "data_uuid": "7568715f03a546a085ff57316bdc0d44"
  },
  "api_key": LUABASE_API_KEY,
  "details": {
    "parameters": {
      "home": {
            "type": "value",
            "value": ""
      },
      "query": {
            "type": "value",
            "value": "satoshi"
      }
}
  }
}
headers = {"content-type": "application/json"}
response = requests.request("POST", url, json=payload, headers=headers)
data = response.json() 
```
