
#### Total tranaction per day per token 

```
with total_transactions_pertoken_perday as(
  select date_trunc(block_timestamp, DAY) as m_block_timestamp, 
  count(*) as total_transactions,
  token_address
  from `bigquery-public-data.crypto_ethereum.token_transfers`
  where DATE(block_timestamp) > DATE_SUB(CURRENT_DATE(), INTERVAL 180 day)

  GROUP by
     date_trunc(block_timestamp, DAY),
    token_address
)

select * from total_transactions_pertoken_perday
```