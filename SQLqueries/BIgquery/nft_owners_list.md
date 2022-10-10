
```
WITH
  genesis AS (
  SELECT
    *
  FROM
    `bigquery-public-data.crypto_ethereum.contracts`
  WHERE
    address = LOWER('0x3Df5c619a4926156f966A64E08f863385C21Da0e')),

added_row_number AS(
  SELECT
    *,
    ROW_NUMBER() OVER(PARTITION BY value ORDER BY block_timestamp DESC) AS row_number
  FROM
    `bigquery-public-data.crypto_ethereum.token_transfers`
  WHERE
    DATE(block_timestamp)  >= DATE((SELECT block_timestamp FROM genesis))
    AND token_address = LOWER('0x3Df5c619a4926156f966A64E08f863385C21Da0e') ),

token_ownership AS (
  SELECT
    CAST(value AS FLOAT64) AS value,
    to_address
  FROM
    added_row_number
  WHERE
    row_number = 1
  ORDER BY
    value DESC ),

result as (
SELECT
  COUNT(1) AS count, to_address
FROM
  token_ownership
GROUP BY
  to_address
ORDER BY
  count DESC )

select * from result 
```