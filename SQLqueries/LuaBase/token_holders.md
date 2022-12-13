### ERC721 token holders : table_name {{home}}.erc721_token_owners
```
WITH genesis AS (
  SELECT *
  FROM
    ethereum.contracts
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

select * from aggregated_wallet_balances
order by balance desc
limit {{limit}}
offset {{offset}}
```
### ERC1155 top holders

```
WITH genesis AS (
  SELECT *
  FROM
    ethereum.contracts
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
        standard = 'erc1155'
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
        standard = 'erc1155'
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

select * from aggregated_wallet_balances
order by balance desc
limit {{limit}}
offset {{offset}}

```

### ERC20 holders 

```
WITH genesis AS (
  SELECT *
  FROM
    ethereum.contracts
  WHERE
    address = LOWER('{{contract_address}}')
  LIMIT 1),

wallet_balances AS (
      SELECT
        toFloat64(value) AS value,
        block_timestamp,
        to_address AS address
      FROM
        ethereum.token_transfers
      WHERE
        DATE(block_timestamp)  >= DATE((SELECT block_timestamp FROM genesis))
        AND token_address =  LOWER('{{contract_address}}')
        AND to_address is not null

      UNION ALL
      SELECT
        -toFloat64(value) AS value,
        block_timestamp,
        from_address AS address
      FROM
       ethereum.token_transfers
      WHERE
        DATE(block_timestamp)  >= DATE((SELECT block_timestamp FROM genesis))
        AND token_address =  LOWER('{{contract_address}}')
        AND from_address is not null 

),

aggregated_wallet_balances AS (
   SELECT
      address,
      round(SUM(value)/pow(10, 18), 4) AS balance
  from wallet_balances
  group by  address
)

select * from aggregated_wallet_balances
order by balance desc
limit {{limit}}
offset {{offset}}
```

