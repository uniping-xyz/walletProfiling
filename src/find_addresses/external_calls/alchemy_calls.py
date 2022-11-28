
import aiohttp
from eth_utils import to_checksum_address
from loguru import logger
async def erc20_wallet_balance(web3_provider,  wallet_address):
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
     }
    
    params = {"jsonrpc": "2.0",
            "method":"alchemy_getTokenBalances", 
            "params": [to_checksum_address(wallet_address)],"id":"1"}
    
    logger.info(params)
    async with aiohttp.ClientSession() as session:
        async with session.post(web3_provider, json=params, headers=headers) as resp:
            response  = await resp.json()
    return response

