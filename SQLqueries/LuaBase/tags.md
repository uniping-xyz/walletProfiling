

```
select DISTINCT(label)
from ethereum.tags
```

```
import requests
import os

LUABASE_API_KEY = os.getenv('LUABASE_API_KEY')

payload = {
  "block": {
    "data_uuid": "958a4cdf11684438942e591e9bdb6e18"
  },
  "api_key": LUABASE_API_KEY,
  "parameters": {
    "label": {
        "value": "defi",
        "type": "value"
    }
}
}
headers = {"content-type": "application/json"}
response = requests.request("POST", url, json=payload, headers=headers)
data = response.json() 
```