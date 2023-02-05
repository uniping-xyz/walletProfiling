

from shroomdk import ShroomDK
import os
sdk = ShroomDK(os.getenv("SHROOM_API_KEY"))



async def eth_erc20_token_holders(token_address, limit, offset):

    query = """
     
      with wallet_balances AS (
            SELECT
              raw_amount,
              block_timestamp,
              to_address AS wallet_address
            FROM
              ETHEREUM.core.fact_token_transfers
            WHERE
              contract_address =  LOWER('%s')
              AND to_address is not null
              AND to_address != '0x0000000000000000000000000000000000000000'

            UNION ALL
            SELECT
              -raw_amount,
              block_timestamp,
              from_address AS wallet_address
            FROM
             ETHEREUM.core.fact_token_transfers
            WHERE
              contract_address =  LOWER('%s')
              AND from_address is not null
              AND from_address != '0x0000000000000000000000000000000000000000'

      ),
     
      aggregated_wallet_balances AS (
         SELECT
            wallet_address,
            sum(raw_amount) as balance
        from wallet_balances
        group by  wallet_address
      )
     
      select * from aggregated_wallet_balances
      order by balance desc
      limit %s
      offset %s
    """%(token_address, token_address, limit, offset)
    query_result_set = sdk.query(query)
    return query_result_set.records
