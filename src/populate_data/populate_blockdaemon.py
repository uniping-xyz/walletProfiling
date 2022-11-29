
import aiohttp
import os
from loguru import logger
import time
import itertools
from find_addresses.external_calls import blockdaemon_calls
from caching.cache_utils import cache_validity, get_cache, set_cache, delete_cache

async def check_blockDaemon_tokens_staleness(app:object):
    caching_key = "blockDaemonTokenListLstUpdate"
    cache_valid = await cache_validity(app.config.REDIS_CLIENT, caching_key, 
                            app.config.CACHING_TTL['LEVEL_FIVE'])

    if not cache_valid:
        app.add_task(populate_erc721_blockdaemon(app))
        app.add_task(populate_erc1155_blockdaemon(app))
        
        await set_cache(app.config.REDIS_CLIENT, caching_key, [])
    return

async def populate_erc721_blockdaemon(app: object):
    result = []
    params = {"token_type": "ERC721", "verified": "true", "page_size": 100}
    headers = {'X-API-Key': os.environ["BLOCK_DAEMON_SECRET"] }
    logger.info(headers)
    total_tokens_fetched = 0
    while True:
        response = await blockdaemon_calls.get_nft_collections(params)

        if response['meta']['paging']['next_page_token'] == "":
            break
        params = {"token_type": "ERC721",
                "page_size": 100,
                 "verified": "true", 
                 "page_token": response['meta']['paging']['next_page_token']}
        logger.success(f"Total tokens fetched are {total_tokens_fetched}")
        for token in response["data"]:
            tokenized_name = [[subname[0:i] for i in range(2, len(subname)+1)] for subname in token["name"].lower().split()]
            tokens = list(itertools.chain(*tokenized_name))
            token.update({"tokens": tokens,  "token_type": "erc721"})
            if not await app.config.ETH_ERC721_TOKENS.find_one({"contracts": token.get('contracts')}):
                await app.config.ETH_ERC721_TOKENS.insert_one(token)
        total_tokens_fetched += 100
        time.sleep(0.2)


    logger.success("Fresh ERC721 token list from blockdaemon retrived successfully")
    return

async def populate_erc1155_blockdaemon(app: object):
    result = []
    params = {"token_type": "ERC1155", "verified": "true", "page_size": 100}
    headers = {'X-API-Key': os.environ["BLOCK_DAEMON_SECRET"] }
    total_tokens_fetched = 0

    while True:
        response = await blockdaemon_calls.get_nft_collections(params)
        if response['meta']['paging']['next_page_token'] == "":
            break
        params = {"token_type": "ERC1155", 
                "verified": "true", 
                "page_size": 100,
                "page_token": response['meta']['paging']['next_page_token']}
        logger.success(f"Total tokens fetched are {total_tokens_fetched}")
        for token in response["data"]:
            tokenized_name = [[subname[0:i] for i in range(2, len(subname)+1)] for subname in token["name"].lower().split()]
            tokens = list(itertools.chain(*tokenized_name))
            token.update({"tokens": tokens, "token_type": "erc1155"})
            if not await app.config.ETH_ERC1155_TOKENS.find_one({"contracts": token.get('contracts')}):
                await app.config.ETH_ERC1155_TOKENS.insert_one(token)
        total_tokens_fetched += 100

    logger.success("Fresh ERC1155 token list from blockdaemon retrived successfully")
    return

