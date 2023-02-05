

from shroomdk import ShroomDK
import os

sdk = ShroomDK(os.getenv("SHROOM_API_KEY"))

def eth_wallet_nft_transfers(wallet_address, days):
    query  = """
        select nft_address, project_name, tokenid, block_timestamp
        from ETHEREUM.core.ez_nft_transfers
        where  block_timestamp >= dateadd('day', -%s, current_date())
        and (nft_from_address = Lower('%s')
        or nft_to_address = Lower('%s'))
        order by block_timestamp desc
    """%(days, wallet_address, wallet_address)
    query_result_set = sdk.query(query)
    return query.records
