
from shroomdk import ShroomDK
import os

sdk = ShroomDK(os.getenv("SHROOM_API_KEY"))

def eth_wallet_tx_per_day(wallet_address, days):
    query  = """
        select date(t.block_timestamp) as tithi,  count(1) as tx_count, sum(eth_value) as eth_spent
        from ETHEREUM.core.fact_transactions  as t
        where  block_timestamp >= dateadd('day', -%s, current_date())
        and (from_address = Lower('%s')
        or to_address = Lower('%s'))
        group by date(t.block_timestamp)
    """%(days, wallet_address, wallet_address )
    query_result_set = sdk.query(query)
    return query.records
