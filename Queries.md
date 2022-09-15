
#### Token aggregation
End result: Token addresses with a list of address that interacted with the smart contract and the balance 
This will not run beyond 60 -70 days since Bigquery has 100 MB limit on rows.
```
  SELECT
  tokens.name,
  tokens.symbol,
  token_address,
  wallet_addresses,
  balance,
  last_active
FROM (
  SELECT
    token_address,
    ARRAY_AGG(address) AS wallet_addresses,
    ARRAY_AGG(CAST(balance AS FLOAT64)) AS balance,
    ARRAY_AGG(last_time) AS last_active
  FROM (
    SELECT
      token_address,
      address,
      MAX(block_timestamp) AS last_time,
      SUM(value) AS balance
    FROM (
      SELECT
        token_address,
        CAST(value AS FLOAT64) AS value,
        block_timestamp,
        to_address AS address
      FROM
        `bigquery-public-data.crypto_ethereum.token_transfers`
      WHERE
        DATE(block_timestamp) > DATE_SUB(CURRENT_DATE(), INTERVAL 1 day)
      UNION ALL
      SELECT
        token_address,
        -CAST(value AS FLOAT64) AS value,
        block_timestamp,
        from_address AS address
      FROM
        `bigquery-public-data.crypto_ethereum.token_transfers`)
    WHERE
      DATE(block_timestamp) > DATE_SUB(CURRENT_DATE(), INTERVAL 1 day)
    GROUP BY
      token_address,
      address)
  GROUP BY
    token_address ) AS contracts
LEFT JOIN
  `pingboxproduction.Address.coingecko-token-list2` AS tokens
ON
  (contracts.token_address = tokens.address)
```

#### Addresses spent most on Gas fee

```
SELECT
  from_address,
  SUM(CAST(receipt_gas_used AS numeric) * CAST(COALESCE(gas_price, receipt_effective_gas_price) AS numeric)) / 1e18 AS total_fees
FROM
  `bigquery-public-data.crypto_ethereum.transactions`
GROUP BY
  from_address
ORDER BY
  total_fees DESC
LIMIT
  100;
```

#### All balances on a single contract address

```
SELECT
  address,
  SUM(value) AS balance
FROM (
  SELECT
    token_address,
    from_address AS address,
    -CAST(value AS bigdecimal) / 1e18 AS value
  FROM
    `bigquery-public-data.crypto_ethereum.token_transfers`
  UNION ALL
  SELECT
    token_address,
    to_address AS address,
    CAST(value AS bigdecimal) / 1e18 AS value
  FROM
    `bigquery-public-data.crypto_ethereum.token_transfers` )
WHERE
  token_address = '0xc18360217d8f7ab5e7c516566761ea12ce7f9d72'
GROUP BY
  address
ORDER BY
  balance DESC;
```

#### balance history - the balance of an address after each transaction
```
SELECT
  block_timestamp AS timestamp,
  address,
  SUM(value) 
    OVER (PARTITION BY address ORDER BY block_timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS balance
FROM (
  SELECT
    block_timestamp,
    token_address,
    from_address AS address,
    -CAST(value AS bigdecimal) / 1e18 AS value
  FROM
    `bigquery-public-data.crypto_ethereum.token_transfers`
  UNION ALL
  SELECT
    block_timestamp,
    token_address,
    to_address AS address,
    CAST(value AS bigdecimal) / 1e18 AS value
  FROM
    `bigquery-public-data.crypto_ethereum.token_transfers` )
WHERE
  token_address = '0xc18360217d8f7ab5e7c516566761ea12ce7f9d72'
ORDER BY
  balance DESC;
```

#### We see this with ENS registration and renewal events; the contract outputs the expiry time, 
    and we may want to 
    know how long the name was registered or renewed for. Analytics queries come in useful here too, 
    this time with the LAG function, which references a previous row in the input set:
```
SELECT
  block_timestamp,
  name,
  CAST(expires AS int64) - COALESCE(LAG(CAST(expires AS int64), 1) 
  OVER(PARTITION BY name ORDER BY block_timestamp), 
  UNIX_SECONDS(block_timestamp)) AS duration
FROM (
  SELECT
    block_timestamp,
    name,
    expires
  FROM
    `blockchain-etl.ethereum_ens.ETHRegistrarController3_event_NameRegistered`
  UNION ALL
  SELECT
    block_timestamp,
    name,
    expires
  FROM
    `blockchain-etl.ethereum_ens.ETHRegistrarController3_event_NameRenewed`)

```