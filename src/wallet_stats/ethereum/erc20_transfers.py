

from shroomdk import ShroomDK
import os

sdk = ShroomDK(os.getenv("SHROOM_API_KEY"))

def eth_wallet_erc20_transfers(wallet_address, days):
    query  = """
        select contract_address, symbol, raw_amount, amount_usd, _inserted_timestamp
        from ETHEREUM.core.ez_token_transfers
        where  _inserted_timestamp >= dateadd('day', -%s, current_date())
        and (origin_from_address = Lower('%s')
        or origin_to_address = Lower('%s'))
        order by _inserted_timestamp desc
    """%(days, wallet_address, wallet_address)
    query_result_set = sdk.query(query)
    return query.records
