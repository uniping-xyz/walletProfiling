
import json
import pymongo
import os
import itertools
ENVIRONMENT = os.environ['APP_ENV']
print (f"This is env {ENVIRONMENT}")

from pycoingecko import CoinGeckoAPI

with open('../config/config.json', 'r') as f:
    config = json.load(f)
    print (config)

db_config = config[ENVIRONMENT]["DATABASE"]
uri = f'mongodb://{db_config["user"]}:{ db_config["password"]}@{db_config["ip"]}:{ db_config["port"]}/{db_config["dbname"]}'
connection = pymongo.MongoClient(uri)
db = connection[db_config["dbname"]]

token_collection = db["tokens"]
print (token_collection)

cg = CoinGeckoAPI()
json_object = {}
result = cg.get_coins_list(include_platform=True)
tokens_list = []
token_collection.drop()

get_platform = lambda platforms, name :  platforms.get(name) if  (platforms.get(name) and platforms.get(name) != '') else None 

for e in result:
    temp = e.copy()
    platforms = temp.pop("platforms")
    
    _platforms = { "ethereum":  get_platform( platforms, "ethereum"),
                    "polygon":  get_platform( platforms, "polygon-pos"),
                    "binance_smart_chain": get_platform( platforms, "binance-smart-chain") }
    if list(_platforms.values()).count(None) == len(_platforms):
        pass
    else:
        temp.update(_platforms)
        name = f'{e["name"]} {e["name"]}'
        tokenized_name = [[subname[0:i] for i in range(2, len(subname)+1)] for subname in name.lower().split()]
        tokens = list(itertools.chain(*tokenized_name))
        temp.update({"tokens": tokens})
        tokens_list.append(temp)

token_collection.insert_many(tokens_list)
