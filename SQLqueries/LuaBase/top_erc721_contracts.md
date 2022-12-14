
### Query
#### Live view name: top_erc721_contracts

```
with total_transactions_pertoken_perday as(
  select count(*) as total_transactions,
  contract_address
  from ethereum.nft_transfers
  WHERE 
    DATE(block_timestamp) > DATE(now()) - toIntervalDay('{{number_of_days}}')
    and standard = '{{standard}}'
  GROUP by
    contract_address
  ORDER BY total_transactions DESC 
),

with_names as (
  select tt.total_transactions, tt.contract_address, pp.address, pp.name, pp.symbol from total_transactions_pertoken_perday as tt
  left join
  ethereum.tokens as pp
  on lower(tt.contract_address) = lower(pp.address)
)
select * from with_names 
LIMIT {{limit}}
OFFSET {{offset}}
```


```
with total_transactions_pertoken_perday as(
  select count(*) as total_transactions,
  contract_address
  from ethereum.nft_transfers
  WHERE 
    DATE(block_timestamp) > DATE(now()) - toIntervalDay('{{number_of_days}}')
    and standard = '{{standard}}'
  GROUP by
    contract_address
  ORDER BY total_transactions DESC 
),

with_names as (
  select tt.total_transactions, tt.contract_address, pp.address, pp.name, pp.symbol from total_transactions_pertoken_perday as tt
  left join
  ethereum.tokens as pp
  on lower(tt.contract_address) = lower(pp.address)
)
select * from with_names 
LIMIT {{limit}}
OFFSET {{offset}}
```