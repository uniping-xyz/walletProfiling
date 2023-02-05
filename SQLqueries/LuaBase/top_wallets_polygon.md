```

with contract_addresses as (select address from polygon.contracts
where is_erc721=1)

select from_address as wallet_address, count(*) as total_transactions
  from polygon.token_transfers
  WHERE  token_address in (select * from contract_addresses)
    and from_address != lower('0x0000000000000000000000000000000000000000')
    and DATE(block_timestamp) > DATE(now()) - toIntervalDay(10)

    group by from_address
order by total_transactions desc
```


