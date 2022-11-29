
import json
import pymongo
import os
import itertools
from caching.cache_utils import cache_validity, get_cache, set_cache, delete_cache
from loguru import logger
from pycoingecko import CoinGeckoAPI
from eth_utils import to_checksum_address

async def check_coingecko_tokens_staleness(app:object):
    caching_key = "coingeckoTokenListLstUpdate"
    cache_valid = await cache_validity(app.config.REDIS_CLIENT, caching_key, 
                            app.config.CACHING_TTL['LEVEL_FIVE'])

    if not cache_valid:
        app.add_task(fetch_coingecko_token_list(app))
        await set_cache(app.config.REDIS_CLIENT, caching_key, [])
    return


#late find a mechanism to shift it to redis rather then using mongo just for this.
async def fetch_coingecko_token_list(app: object):
    logger.info("Fetching fresh token list from coingecko")
    cg = CoinGeckoAPI()
    result = cg.get_coins_list(include_platform=True)
    

    get_platform = lambda platforms, name :  platforms.get(name) if  (platforms.get(name) and platforms.get(name) != '') else None 

    for token in result:
        temp = token.copy()
        platforms = temp.pop("platforms")
        
        name = f'{token["name"]} {token["name"]}'
        tokenized_name = [[subname[0:i] for i in range(2, len(subname)+1)] for subname in name.lower().split()]
        tokens = list(itertools.chain(*tokenized_name))

        if get_platform(platforms, "ethereum"):
            contract_address = get_platform(platforms, "ethereum")
            contract_address = to_checksum_address(contract_address)

            _token = {"contracts" : contract_address, 
                            "tokens": tokens, 
                            "id": token.get("id") , 
                            "symbol": token.get("symbol"), 
                            "name": token.get("name"),
                            "token_type":  "erc20"}
            if not await app.config.ETH_ERC20_TOKENS.find_one({"contracts": contract_address}):
                logger.info(f"Inserting new token in ETH_ERC20_TOKENS [{contract_address}]")
                await app.config.ETH_ERC20_TOKENS.insert_one(_token)

        if get_platform(platforms, "polygon"):
            contract_address = get_platform(platforms, "polygon")
            contract_address = to_checksum_address(contract_address)
            _token = {"contracts" : contract_address, 
                    "tokens": tokens,
                    "id": token.get("id"), 
                    "symbol": token.get("symbol"), 
                    "name": token.get("name"),
                    "token_type": "erc20"}
            if not await app.config.POLYGON_ERC20_TOKENS.find_one({"contracts":  contract_address}):
                await app.config.POLYGON_ERC20_TOKENS.insert_one(_token)

    logger.success("Coingecko ERC20 list retrived successfully")
    return 
