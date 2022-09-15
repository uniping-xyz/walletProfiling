

def token_wallet_aggregation():
    #this gives you the token_address and all the addresses who have interacted with 
    # in the time period and also the balances that wallet addresses has maintained 
    # on them in the timeperiod. 

SELECT
  token_address,
  wallet_addresses,
  balance,
  tokens.name,
  tokens.symbol
FROM (
  SELECT
    token_address,
    ARRAY_AGG(address) AS wallet_addresses,
    ARRAY_AGG(CAST(balance AS FLOAT64)) AS balance
  FROM (
    SELECT
      token_address,
      address,
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
        DATE(block_timestamp) > DATE_SUB(CURRENT_DATE(), INTERVAL 60 day)
      UNION ALL
      SELECT
        token_address,
        -CAST(value AS FLOAT64) AS value,
        block_timestamp,
        from_address AS address
      FROM
        `bigquery-public-data.crypto_ethereum.token_transfers`)
    WHERE
      DATE(block_timestamp) > DATE_SUB(CURRENT_DATE(), INTERVAL 60 day)
    GROUP BY
      token_address,
      address )
  GROUP BY
    token_address ) AS contracts
JOIN
  `bigquery-public-data.crypto_ethereum.tokens` AS tokens
ON
  (contracts.token_address = tokens.address)

def token_wallet_aggregation_with_last_active():
    #this gives you the token_address and all the addresses who have interacted with 
    # in the time period and also the balances that wallet addresses has maintained 
    # on them in the timeperiod. 

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
JOIN
  `bigquery-public-data.crypto_ethereum.tokens` AS tokens
ON
  (contracts.token_address = tokens.address)