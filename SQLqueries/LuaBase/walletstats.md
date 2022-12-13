select block_timestamp, from_address, to_address, value_eth, transaction_fee_eth
from ethereum.transactions as t 
where  block_timestamp >= date(date_sub(day, {{days}}, now())) 
and (from_address == Lower('{{wallet_address}}')
or to_address == Lower('{{wallet_address}}'))




## wallettransactionsperday
```
select date(t.block_timestamp) as tithi,  count(1) as tx_count, sum(value_eth) as eth_spent
from ethereum.transactions as t 
where  block_timestamp >= date(date_sub(day, {{days}}, now())) 
and (from_address == Lower('{{wallet_address}}')
or to_address == Lower('{{wallet_address}}'))
group by date(t.block_timestamp)
```


## mostoutgoingtransactions
```

with all_interactions as (select *
    from ethereum.transactions as t 
    where  block_timestamp >= date(date_sub(day, {{days}}, now())) 
    and (to_address == Lower('{{wallet_address}}')
    or from_address == Lower('{{wallet_address}}'))),

-- select * from all_interactions

agg as (select count(to_address) as outgoing_tx_count, to_address
    from all_interactions
    where from_address == Lower('{{wallet_address}}')
    group by to_address
    order by outgoing_tx_count desc
)

select t.outgoing_tx_count, t.to_address,  pp.name from agg as t
  left join
  ethereum.tokens as pp
  on lower(t.to_address) = lower(pp.address)

```


## mostincomingtransactions

with all_interactions as (select *
    from ethereum.transactions as t 
    where  block_timestamp >= date(date_sub(day, {{days}}, now())) 
    and (to_address == Lower('{{wallet_address}}')
    or from_address == Lower('{{wallet_address}}'))),

agg as (select count(from_address) as incoming_tx_count, from_address
    from all_interactions
    where to_address == Lower('{{wallet_address}}')
    group by from_address
    order by incoming_tx_count desc
)

select t.incoming_tx_count, t.from_address,  pp.name from agg as t
  left join
  ethereum.tokens as pp
  on lower(t.from_address) = lower(pp.address)
```
