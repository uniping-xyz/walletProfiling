

## All time top erc20
```
with total_transactions_pertoken_perday as(
  select count(*) as total_transactions,
  token_address
  from {{chain}}.token_transfers
  WHERE 
    token_address NOT IN (SELECT DISTINCT contract_address FROM {{chain}}.nft_transfers)
  GROUP by
    token_address
  ORDER BY total_transactions DESC 
),

with_names as (
  select distinct tt.total_transactions, tt.token_address as contract_address, pp.address, pp.name, pp.symbol from total_transactions_pertoken_perday as tt
  left join
  ethereum.tokens as pp
  on lower(tt.token_address) = lower(pp.address)
)
select * from with_names
```


## All time top erc721

```
with total_transactions_pertoken_perday as(
  select count(*) as total_transactions,
  contract_address
  from {{chain}}.nft_transfers
  WHERE 
    standard = 'erc721'
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

```

## All time top erc1155

```
with total_transactions_pertoken_perday as(
  select count(*) as total_transactions,
  contract_address
  from {{chain}}.nft_transfers
  WHERE 
    standard = 'erc1155'
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
```