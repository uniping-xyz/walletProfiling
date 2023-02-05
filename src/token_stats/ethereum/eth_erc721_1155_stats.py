
from shroomdk import ShroomDK
import os
sdk = ShroomDK(os.getenv("SHROOM_API_KEY"))

nft_sales = """
    select
      platform_name,
      seller_address,
      buyer_address,
      price_usd,
      block_timestamp
    from
      ETHEREUM.core.ez_nft_sales
    where
      nft_address = Lower('0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D')
      and DATE(block_timestamp) >= dateadd('day', -30,  current_date())
    order by
       block_timestamp
    """


"""
This table contains NFT events on the Ethereum blockchain. It currently supports sales on 
Opensea, Seaport, Blur, Larva Labs, LooksRare, Rarible, x2y2, Sudoswap, and NFTX. 
More data and exchanges will be added over time.
"""
async def get_nft_sales_on_platforms(token_address, days):
    query = f"""
    select
      platform_name,
      seller_address,
      buyer_address,
      price_usd,
      block_timestamp
    from
      ETHEREUM.core.ez_nft_sales
    where
      nft_address = Lower('%s')
      and DATE(block_timestamp) >= dateadd('day', %s,  current_date())
    order by
       block_timestamp
    """%(token_address, -days)
    query_result_set = sdk.query(query)
    return query_result_set.records



async def get_nft_metadata(token_address):
    query = f"""
    SELECT *
         FROM
             ETHEREUM.core.dim_nft_metadata
         WHERE
             contract_address = LOWER('%s')
             and blockchain = 'ethereum'
         LIMIT 1
         """%(token_address)
    query_result_set = sdk.query(query)
    return query_result_set.records