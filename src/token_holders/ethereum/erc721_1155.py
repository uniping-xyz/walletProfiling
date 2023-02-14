
from shroomdk import ShroomDK
import os
from loguru import logger
sdk = ShroomDK(os.getenv("SHROOM_API_KEY"))
"""
   query = WITH genesis AS (
       SELECT *
       FROM
         ETHEREUM.core.dim_contracts_extended
       WHERE
         address = LOWER('%s')
       LIMIT 1),
    
     wallet_balances AS (
           SELECT
             tokenid,
             block_timestamp,
             nft_to_address as wallet_address
           FROM
             ETHEREUM.core.ez_nft_transfers
           WHERE
             block_timestamp  >= (SELECT block_timestamp FROM genesis)
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
             block_timestamp  >= (SELECT block_timestamp FROM genesis)
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
"""
"""
  count(*) as total,
  (CAST(    count_if (total_erc721_assets < 2)                                as decimal(15,3) ) *100)/count(*)  AS less_than_2,

  (CAST(   count_if(total_erc721_assets >= 2   and total_erc721_assets < 5   ) as decimal(15,3))  *100)/count(*) AS one_to_4,
  (CAST(   count_if(total_erc721_assets >= 5   and total_erc721_assets < 10  ) as decimal(15,3))                   *100)/count(*) AS five_to_9,
  (CAST(   count_if(total_erc721_assets >= 10  and total_erc721_assets < 20  ) as decimal(15,3))                  *100)/count(*) AS ten_to_19,
  (CAST(   count_if(total_erc721_assets >= 20  and total_erc721_assets < 50  ) as decimal(15,3))                   *100)/count(*) AS twenty_to_49,
  (CAST(   count_if(total_erc721_assets >= 50  and total_erc721_assets < 100 ) as decimal(15,3))                   *100)/count(*) AS fifty_to_99,
  (CAST(   count_if(total_erc721_assets >= 100 and total_erc721_assets < 200 ) as decimal(15,3))                   *100)/count(*) AS hundred_to_199,
  (CAST(   count_if(total_erc721_assets >= 200 and total_erc721_assets < 500 ) as decimal(15,3))                   *100)/count(*) AS twohundred_to_499,
  (CAST(   count_if(total_erc721_assets >= 500)                                 as decimal(15,3))                 *100)/count(*) AS more_than_500
"""

"""
  COUNT(*) AS total,
  (
    CAST(count_if(total_erc721_assets < 2) AS DECIMAL(15, 2)) * 100
  ) / COUNT(*) AS less_than_2,
  (
    count_if(
      total_erc721_assets >= 2
      AND total_erc721_assets < 5
    ) * 100
  ) / COUNT(*) AS one_to_4,
  (
    count_if(
      total_erc721_assets >= 5
      AND total_erc721_assets < 10
    ) * 100
  ) / COUNT(*) AS five_to_9,
  (
    count_if(
      total_erc721_assets >= 10
      AND total_erc721_assets < 20
    ) * 100
  ) / COUNT(*) AS ten_to_19,
  (
    count_if(
      total_erc721_assets >= 20
      AND total_erc721_assets < 50
    ) * 100
  ) / COUNT(*) AS twenty_to_49,
  (
    count_if(
      total_erc721_assets >= 50
      AND total_erc721_assets < 100
    ) * 100
  ) / COUNT(*) AS fifty_to_99,
  (
    count_if(
      total_erc721_assets >= 100
      AND total_erc721_assets < 200
    ) * 100
  ) / COUNT(*) AS hundred_to_199,
  (
    count_if(
      total_erc721_assets >= 200
      AND total_erc721_assets < 500
    ) * 100
  ) / COUNT(*) AS twohundred_to_499,
  (count_if(total_erc721_assets >= 500) * 100) / COUNT(*) AS more_than_500


"""

async def eth_erc721_1155_token_holders(token_address, limit, offset):

    query = """
     with wallet_balances AS (
           SELECT
             tokenid,
             block_timestamp,
             nft_to_address as wallet_address
           FROM
             ETHEREUM.core.ez_nft_transfers
           WHERE
             nft_address =  LOWER('%s')
             AND nft_to_address is not null
             AND nft_to_address != '0x0000000000000000000000000000000000000000'
    
           UNION ALL
           SELECT
             -tokenid,
             block_timestamp,
             nft_from_address as wallet_address
           FROM
            ETHEREUM.core.ez_nft_transfers
           WHERE
             nft_address =  LOWER('%s')
             AND nft_from_address is not null
            AND nft_from_address != '0x0000000000000000000000000000000000000000'

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
     """%(token_address, token_address, limit, offset)

    logger.info(query)
    query_result_set = sdk.query(query)
    return query_result_set.records


"""
There are total 5097206 on ethereum blockchains that holds at least 1 NFT 

41.395% addresses hold 1 NFT	
25.743% addresses hold 1 - to 4 NFT
11.981% addresses hold 5 to 9 NFTs
8.193% addresses hold 10 to 19 NFTs
6.64 % addresses hold 20 to 49 NFTs
2.844% addresses hold 50 to 99 NFTs
1.644% addresses golds 100 to 199 NFTs
1.5% addrsses holds 200 to 5000 NFTs 
0.011% addresses holds more than 10000 NFTs

These stats excludes all erc1155 tokens. 
There are total of  around 3.5 million addresses only on ethereum that holds less than 10 NFTs. 

"""