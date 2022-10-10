
#### TOken stats for a given period of time. 

```
with transactions AS (
select *
  from `pingboxproduction.Address.total_transactions_pertoken_perday`
  where token_address = lower("0xdAC17F958D2ee523a2206206994597C13D831ec7")

),

unique_addresses AS (
  select *
    from `pingboxproduction.Address.unique_addresses_pertoken_perday`
    where token_address = lower("0xdAC17F958D2ee523a2206206994597C13D831ec7")

)

select transactions.m_block_timestamp as date, transactions.total_transactions, unique_addresses.unique_addresses from
 transactions
JOIN
  unique_addresses 
ON transactions.m_block_timestamp = unique_addresses.m_block_timestamp

ORDER BY
    transactions.m_block_timestamp

```