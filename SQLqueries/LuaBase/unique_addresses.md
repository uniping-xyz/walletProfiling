WITH genesis AS (
  SELECT *
  FROM
    {{chain}}.contracts
  WHERE
    address = LOWER('{{contract_address}}')
  LIMIT 1),

wallet_balances AS (
      SELECT
        toInt64(1) AS value,
        block_timestamp,
        to AS address
      FROM
        ethereum.nft_transfers
      WHERE
        standard = 'erc721'
        AND DATE(block_timestamp)  >= DATE((SELECT block_timestamp FROM genesis))
        AND contract_address =  LOWER('{{contract_address}}')
        AND to is not null

      UNION ALL
      SELECT
        -toInt64(1) AS value,
        block_timestamp,
        from AS address
      FROM
       ethereum.nft_transfers
      WHERE
        standard = 'erc721'
        AND DATE(block_timestamp)  >= DATE((SELECT block_timestamp FROM genesis))
        AND contract_address =  LOWER('{{contract_address}}')
        AND from is not null
),

aggregated_wallet_balances AS (
   SELECT
      address,
      SUM(value) AS balance
  from wallet_balances
  group by  address
)


select * from wallet_balances