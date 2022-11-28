
from eth_utils import to_checksum_address



async def search_contract_address(app, contract_address):
    contract_address = to_checksum_address(contract_address)
    result = await app.config.ETH_ERC1155_TOKENS.find_one({"contracts": contract_address},
                projection={"_id": False, "tokens": False})
    return result

async def search_text(app, text):
    result = []
    cursor = app.config.ETH_ERC1155_TOKENS.find({"tokens": text}, projection={"_id": False, "tokens": False})
    async for document in cursor:
        result.append(document)
    return result