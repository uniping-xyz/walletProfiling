
### Total unique addresses per token per day

#### Create Table

```
CREATE TABLE Address.unique_addresses_pertoken_perday
(
  token_address STRING,
  unique_addresses INT64,
  m_block_timestamp TIMESTAMP
)

PARTITION BY
  DATE(m_block_timestamp)

```

```
with wallet_balances AS (
      SELECT
        token_address,
        CAST(value AS FLOAT64) AS value,
        block_timestamp,
        to_address AS address
      FROM
        `bigquery-public-data.crypto_ethereum.token_transfers`
      WHERE
        DATE(block_timestamp) > DATE_SUB(CURRENT_DATE(), INTERVAL 180 day)
        AND to_address is not null 
        AND CAST(value AS FLOAT64) > 0

      UNION ALL
      SELECT
        token_address,
        -CAST(value AS FLOAT64) AS value,
        block_timestamp,
        from_address AS address
      FROM
        `bigquery-public-data.crypto_ethereum.token_transfers`
    WHERE
      DATE(block_timestamp) > DATE_SUB(CURRENT_DATE(), INTERVAL 180 day)
        AND to_address is not null 
        AND CAST(value AS FLOAT64) > 0
),

aggregated_wallet_balances_per_day AS (
   SELECT
      token_address,
      address,
      date_trunc(block_timestamp, DAY) as m_block_timestamp,
      SUM(value) AS balance
  from wallet_balances
  GROUP BY
      token_address,
      address,
      date_trunc(block_timestamp, DAY)
),



aggregated_wallet_balances AS (
   SELECT
      token_address,
      address,
      MAX(m_block_timestamp) AS last_transacted,
      SUM(balance) AS balance
  from aggregated_wallet_balances_per_day
  GROUP BY
      token_address,
      address
),


total_unique_addresses as(

  select m_block_timestamp, token_address, count(DISTINCT address) as unique_addresses from aggregated_wallet_balances_per_day
  GROUP by
    m_block_timestamp,
    token_address
)

select *
from  
total_unique_addresses 
```