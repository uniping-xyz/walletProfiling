
## ethereum.contracts

block_number	UInt64					
block_timestamp	DateTime					
block_hash	String					
address	String					
bytecode	String					
function_sighashes	Array(String)					
is_erc20	UInt8					
is_erc721	UInt8					
is_erc1155	UInt8					




## ethereum.domains
block_number	UInt64					
block_timestamp	DateTime					
block_hash	String					
transaction_hash	String					
transaction_index	Int64					
log_index	UInt64					
contract_address	String					
owner	String					
cost	UInt256					
cost_eth	Float64


## ethereum.nft_transfers

block_number	UInt64					
block_timestamp	DateTime					
block_hash	String					
transaction_hash	String					
transaction_index	Int64					
log_index	UInt64					
contract_address	String					
operator	Nullable(String)					
from	String					
to	String


## ethereum.token_transfers
block_number	UInt64					
block_timestamp	DateTime					
block_hash	String					
transaction_hash	String					
log_index	UInt64					
token_address	String					
from_address	String					
to_address	String					
value	UInt256


##wallet_addresss, total_transactions