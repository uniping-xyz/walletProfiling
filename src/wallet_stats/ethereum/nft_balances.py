


from find_addresses.db_calls.erc721.ethereum import search_contract_address as erc721_eth_search
from find_addresses.db_calls.erc1155.ethereum import search_contract_address as erc1155_eth_search
from find_addresses.external_calls import blockdaemon_calls



"""
Get assets related to a wallet address from Block Daemon
"""
async def eth_nft_balance(app, request_args) -> list:

    response = await blockdaemon_calls.get_eth_nft_balance(request_args.get("wallet_address"), request_args.get("next_page_token"))

    if not response:
        return []

    result = []
    for token in response["data"]:
        contract_address = token.get("contract_address")
        res = await erc721_eth_search(app, contract_address)
        if res:
            token.update({"contract_name": res.get("name")})
        else:
            res = await erc1155_eth_search(app, contract_address)
            if res:
                token.update({"contract_name": res.get("name")})
        if token.get("contract_name") or token.get("name") != "":
            result.append(token)
    
    if response.get('meta'):
        if response.get('meta').get('paging'):
            next_page_token = response['meta']['paging']['next_page_token']
    else:
            next_page_token = None

    return {"result": result, "next_page_token": next_page_token}
