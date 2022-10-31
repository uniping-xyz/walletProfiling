
import json
import pymongo
import os
import itertools
from caching.cache_utils import cache_validity, get_cache, set_cache, delete_cache
from loguru import logger
from pycoingecko import CoinGeckoAPI


async def check_coingecko_tokens_staleness(app:object):
    caching_key = "coingeckoTokenListLstUpdate"
    cache_valid = await cache_validity(app.config.REDIS_CLIENT, caching_key, 
                            app.config.CACHING_TTL['LEVEL_FIVE'])

    if not cache_valid:
        await fetch_coingecko_token_list(app)
        await set_cache(app.config.REDIS_CLIENT, caching_key, [])
    return


#late find a mechanism to shift it to redis rather then using mongo just for this.
async def fetch_coingecko_token_list(app: object):
    logger.info("Fetching fresh token list from coingecko")
    cg = CoinGeckoAPI()
    json_object = {}
    result = cg.get_coins_list(include_platform=True)
    tokens_list = []
    

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
    app.config.TOKENS.drop()
    app.config.TOKENS.insert_many(tokens_list)
    logger.success("Fresh token list from coingecko retrived successfully")
    return 
