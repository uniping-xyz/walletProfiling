


from utils.errors import CustomError
from eth_utils import to_checksum_address
import os
import aiohttp

async def get_nft_collections(params):
    headers = {'X-API-Key': os.environ["BLOCK_DAEMON_SECRET"] }
    async with aiohttp.ClientSession() as session:
        async with session.get("https://svc.blockdaemon.com/nft/v1/ethereum/mainnet/collections", params=params, headers=headers) as resp:
            response  = await resp.json()
    return response



async def get_eth_nft_balance(wallet_address, next_page_token=None):

    params = {
            "wallet_address": to_checksum_address(wallet_address),
            "page_size": 100,
            "verified": "true"}

    if next_page_token:
        params.update({"page_token": next_page_token})
    
    headers = {'X-API-Key': os.environ["BLOCK_DAEMON_SECRET"] }
    
    url = f"https://svc.blockdaemon.com/nft/v1/ethereum/mainnet/assets"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=headers) as resp:
            response  = await resp.json()

    return response

async def get_nft_collection_details(contract_address):
    headers = {'X-API-Key': os.environ["BLOCK_DAEMON_SECRET"] }
    params = {"contract_address": contract_address}
    async with aiohttp.ClientSession() as session:
        async with session.get("https://svc.blockdaemon.com/nft/v1/ethereum/mainnet/collection", params=params, headers=headers) as resp:
            response  = await resp.json()
    return response

