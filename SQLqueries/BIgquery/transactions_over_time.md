
```
with genesis AS (select * from  `bigquery-public-data.crypto_ethereum.contracts`
WHERE address = lower('0x3Df5c619a4926156f966A64E08f863385C21Da0e'))


select 
   DATE(TIMESTAMP_TRUNC(block_timestamp, DAY, "UTC")) as date,
   count(1) as tx_count
from  `bigquery-public-data.crypto_ethereum.token_transfers`
where DATE(block_timestamp) >=  DATE((select block_timestamp from genesis))
AND token_address = lower('0x3Df5c619a4926156f966A64E08f863385C21Da0e')
GROUP BY DATE(TIMESTAMP_TRUNC(block_timestamp, DAY, "UTC"))
```