



from shroomdk import ShroomDK
import os

sdk = ShroomDK(os.getenv("SHROOM_API_KEY"))

async def eth_wallet_label(wallet_address):
    query  = """SELECT *
         FROM
             ETHEREUM.core.dim_labels
         WHERE
             address = '%s'
         """%(wallet_address)
    query_result_set = sdk.query(query)
    return query_result_set.records