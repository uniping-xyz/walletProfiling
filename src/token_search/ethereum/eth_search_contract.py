
from shroomdk import ShroomDK
import os
sdk = ShroomDK(os.getenv("SHROOM_API_KEY"))

async def eth_contract_details(contract_address):
    search_contract = f"""
        SELECT *
             FROM
                 ETHEREUM.core.dim_contracts_extended
             WHERE
                 contract_address = LOWER('%s')
             LIMIT 1
        """%(contract_address)

    query_result_set = sdk.query(search_contract)
    return query_result_set.records

async def eth_contract_on_text(text):
    search_contract = f"""
        SELECT *
             FROM
                 ETHEREUM.core.dim_contracts_extended
             WHERE
                 name like '%s%'
        """%(text)

    query_result_set = sdk.query(search_contract)
    return query_result_set.records
