
etherc721contractcreators
"""
with contracts as (select block_hash, address from ethereum.contracts
where is_erc721=1
and DATE(block_timestamp) > DATE(now()) - toIntervalDay(120)),


txs as (select block_hash, receipt_contract_address, from_address, block_number, block_timestamp from ethereum.transactions
where  DATE(block_timestamp) > DATE(now()) - toIntervalDay(120)
and receipt_contract_address is not null),

-- select * from txs


contract_creators as (select t.block_hash, t.receipt_contract_address as contract_address, t.from_address as wallet_address, t.block_timestamp from contracts as c
join txs as t
on t.block_hash = c.block_hash
and t.receipt_contract_address = c.address)

select count(*) as count, wallet_address from contract_creators
group by wallet_address
order by count desc

"""

etherc1155contractcreators
"""
with contracts as (select block_hash, address from ethereum.contracts
where is_erc1155=1
and DATE(block_timestamp) > DATE(now()) - toIntervalDay(120)),


txs as (select block_hash, receipt_contract_address, from_address, block_number, block_timestamp from ethereum.transactions
where  DATE(block_timestamp) > DATE(now()) - toIntervalDay(120)
and receipt_contract_address is not null),

-- select * from txs


contract_creators as (select t.block_hash, t.receipt_contract_address as contract_address, t.from_address as wallet_address, t.block_timestamp from contracts as c
join txs as t
on t.block_hash = c.block_hash
and t.receipt_contract_address = c.address)

select count(*) as count, wallet_address from contract_creators
group by wallet_address
order by count desc
"""


ethnostandardscontractcreators
"""
with contracts as (select block_hash, address from ethereum.contracts
where is_erc20=0 and is_erc1155 = 0 and is_erc721 = 0
and DATE(block_timestamp) > DATE(now()) - toIntervalDay(120)),


txs as (select block_hash, receipt_contract_address, from_address, block_number, block_timestamp from ethereum.transactions
where  DATE(block_timestamp) > DATE(now()) - toIntervalDay(120)
and receipt_contract_address is not null),

-- select * from txs


contract_creators as (select t.block_hash, t.receipt_contract_address as contract_address, t.from_address as wallet_address, t.block_timestamp from contracts as c
join txs as t
on t.block_hash = c.block_hash
and t.receipt_contract_address = c.address)

select count(*) as count, wallet_address from contract_creators
group by wallet_address
order by count desc
"""

etherc20contractcreators
"""
with contracts as (select block_hash, address from ethereum.contracts
where is_erc20=1
and DATE(block_timestamp) > DATE(now()) - toIntervalDay(120)),


txs as (select block_hash, receipt_contract_address, from_address, block_number, block_timestamp from ethereum.transactions
where  DATE(block_timestamp) > DATE(now()) - toIntervalDay(120)
and receipt_contract_address is not null),

-- select * from txs


contract_creators as (select t.block_hash, t.receipt_contract_address as contract_address, t.from_address as wallet_address, t.block_timestamp from contracts as c
join txs as t
on t.block_hash = c.block_hash
and t.receipt_contract_address = c.address)

select count(*) as count, wallet_address from contract_creators
group by wallet_address
order by count desc
"""