
import os
from loguru import logger
from populate_data.populate_coingecko import check_coingecko_tokens_staleness
from populate_data.populate_blockdaemon import  check_blockDaemon_tokens_staleness
from find_addresses.db_calls.erc20.ethereum import search_contract_address as erc20_eth_search
from find_addresses.external_calls import alchemy_calls



async def eth_erc20_balance(app, request_args) -> list:
    await check_coingecko_tokens_staleness(app)
    await check_blockDaemon_tokens_staleness(app) ##this checks if the coingecko token list in db is not older than 5 hours
    response = await alchemy_calls.erc20_wallet_balance(os.environ["ETH_WALLET_BALANCE_URL"],  request_args.get("wallet_address"))
    result = []

    for e in response["result"]["tokenBalances"]:
        contract_address = e["contractAddress"]
        token_balance = e["tokenBalance"]
        contract_name =  await erc20_eth_search(app, contract_address)
        logger.info(contract_name)
        if contract_name:
            token_balance = token_balance.replace("0x", "")
            if token_balance:
                try:
                    balance = int(token_balance, 16)/10**18
                    if not round(balance, 2) <= 0.0:
                        result.append({"contract_address": contract_address, "contract_name": contract_name, "balance": round(balance, 3)})
                except Exception:
                    continue
    return result

