from shroomdk import ShroomDK
import os

sdk = ShroomDK(os.getenv("SHROOM_API_KEY"))

async def eth_millionaires_dex():

    query = """with wallet_millionaire as (
      select
          distinct address
      from crosschain.core.address_tags
      where tag_name = 'wallet millionaire'
          and creator = 'flipside'
      )
      select
        distinct address,
        tag_name
      from crosschain.core.address_tags
      where
          tag_type = 'dex'
          and address in (select distinct address from wallet_millionaire)
          and creator = 'flipside'
      """

    query_result_set = sdk.query(query)
    return query_result_set.records