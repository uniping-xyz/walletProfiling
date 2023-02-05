

from shroomdk import ShroomDK
import os
sdk = ShroomDK(os.getenv("SHROOM_API_KEY"))




def eth_erc20_token_holders(token_address, limit, offset):

    query = """WITH genesis AS (
        SELECT *
        FROM
          ETHEREUM.core.dim_contracts_extended
        WHERE
          contract_address = LOWER('%s')
        LIMIT 1),
     
      wallet_balances AS (
            SELECT
              raw_amount,
              block_timestamp,
              to_address AS wallet_address
            FROM
              ETHEREUM.core.fact_token_transfers
            WHERE
              DATE(block_timestamp)  >= DATE((SELECT block_timestamp FROM genesis))
              AND contract_address =  LOWER('%s')
              AND to_address is not null
     
            UNION ALL
            SELECT
              -raw_amount,
              block_timestamp,
              from_address AS wallet_address
            FROM
             ETHEREUM.core.fact_token_transfers
            WHERE
              DATE(block_timestamp)  >= DATE((SELECT block_timestamp FROM genesis))
              AND contract_address =  LOWER('%s')
              AND from_address is not null
     
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
    """%(token_address, token_address, token_address, limit, offset)
    query_result_set = sdk.query(query)
    return query_result_set.records
