
from shroomdk import ShroomDK
import os
sdk = ShroomDK(os.getenv("SHROOM_API_KEY"))

async def eth_contract_details(contract_address):
    search_contract = f"""
        SELECT *
             FROM
                 ETHEREUM.core.dim_contracts_extended
             WHERE
                 (contract_address = LOWER('%s') or 
                 logic_address = Lower('%s'))
             LIMIT 1
        """%(contract_address)

    query_result_set = sdk.query(search_contract)
    return query_result_set.records


async def is_nft_contract(contract_address):
    search_contract = f"""
        SELECT *
           FROM
               ETHEREUM.core.ez_nft_transfers
            where nft_address = lower('%s')
           limit 1
        """%(contract_address)

    query_result_set = sdk.query(search_contract)
    res = query_result_set.records
    if not res:
        return False

    if res.get("erc1155_value"):
        return "erc1155"
    
    return "erc721"


async def is_erc20_contract(contract_address):
    search_contract = f"""
        SELECT *
           FROM
               ETHEREUM.core.ez_token_transfers
            where contract_address = lower('%s')
           limit 1
        """%(contract_address)

    query_result_set = sdk.query(search_contract)
    res = query_result_set.records
    if not res:
        return False
    return "erc20"




async def eth_contract_on_text(text):
    query = f"{text}%"
    search_contract = f"""
        SELECT *
             FROM
                 ETHEREUM.core.dim_contracts_extended
             WHERE
                 name like '%s'
              limit 10
        """%(query)

    query_result_set = sdk.query(search_contract)
    return query_result_set.records
