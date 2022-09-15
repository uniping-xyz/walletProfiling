
from pycoingecko import CoinGeckoAPI
import json
cg = CoinGeckoAPI()
json_object = {}
result = cg.get_coins_list(include_platform=True)
tokens_list = []

for e in result:
    temp = e.copy()
    platforms = temp.pop("platforms")
    _platforms = { "ethereum":  platforms.get("ethereum"),
                    "polygon": platforms.get("polygon-pos"),
                    "binance_smart_chain":  platforms.get("binance-smart-chain") }
    if list(_platforms.values()).count(None) == len(_platforms):
        print (_platforms)
    else:
        temp.update(_platforms)
        tokens_list.append(temp)

with open('coingecko-token-list.json', 'w') as f:
    f.write(json.dumps(tokens_list, indent=4))

def table_schema():
    SCHEMA = """
            [
            {
                "name": "name",
                "type": "STRING",
                "mode": "REQUIRED",
                "description": "name of the token"
            },
            {
                "name": "polygon",
                "type": "STRING",
                "mode": "NULLABLE",
                "description": "contract address on polygon"
            },
                {
                "name": "ethereum",
                "type": "STRING",
                "mode": "NULLABLE",
                "description": "contract address on ethereum"
            },
                {
                "name": "symbol",
                "type": "STRING",
                "mode": "NULLABLE",
                "description": "contract symbol"
            },
            {
                "name": "id",
                "type": "STRING",
                "mode": "NULLABLE",
                "description": "contract id"
            }
            ]

            """
    return SCHEMA