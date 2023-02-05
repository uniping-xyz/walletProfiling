
from shroomdk import ShroomDK
import os
sdk = ShroomDK(os.getenv("SHROOM_API_KEY"))


def eth_erc721_1155_token_holders(token_address, limit, offset):
    query = """WITH genesis AS (
       SELECT *
       FROM
         ETHEREUM.core.dim_nft_metadata
       WHERE
         contract_address = LOWER('%s')
         and blockchain = 'ethereum'
       LIMIT 1),
    
     wallet_balances AS (
           SELECT
             tokenid,
             block_timestamp,
             nft_to_address as wallet_address
           FROM
             ETHEREUM.core.ez_nft_transfers
           WHERE
             block_timestamp  >= (SELECT created_at_timestamp FROM genesis)
             AND nft_address =  LOWER('%s')
             AND nft_to_address is not null
    
           UNION ALL
           SELECT
             -tokenid,
             block_timestamp,
             nft_from_address as wallet_address
           FROM
            ETHEREUM.core.ez_nft_transfers
           WHERE
             block_timestamp  >= (SELECT created_at_timestamp FROM genesis)
             AND nft_address =  LOWER('%s')
             AND nft_from_address is not null
     ),
    
     aggregated_wallet_balances AS (
        SELECT
           wallet_address,
           Count(*) AS balance
       from wallet_balances
       group by wallet_address
     )
    
     select * from aggregated_wallet_balances
     order by balance desc
     Limit %s
     offset %s
     """%(token_address, token_address, token_address, limit, offset)

    query_result_set = sdk.query(query)
    return query_result_set.records
