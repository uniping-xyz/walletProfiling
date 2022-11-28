
### Big query setup codelab example
https://codelabs.developers.google.com/codelabs/cloud-bigquery-python#3

# WalletProfiling

## ------------------ BIg Query setup -------------------------------------------- ## 

### Step 1:

##### Create a partitoned table where your dat awill be dumped

This table is partitoned at last_transacted which is a TIMESTAMP data type.
```
CREATE TABLE Address.eth_token_interaction_partitioned
(
  name STRING,
  symbol STRING,
  token_address STRING,
  wallet_address STRING,
  balance FLOAT64,
  last_transacted TIMESTAMP

)
PARTITION BY
  DATE(last_transacted)
AS (

  SELECT name, symbol, token_address, wallet_address, balance, last_transacted 
        FROM `pingboxproduction.Address.eth-token-interaction`
)
```
### Step 2:
##### You need to fetch all the tokens data from the coingecko.
First create a dataset with the name "Address"
use table_Schema and make a new table on Big query with the name `coingecko-token-list2`
Use `populate_coingecko_token_list.py` script to fetch all the tokens and 
save the result in json format locally.
NOw while creating `coingecko-token-list2` table, upload this file.

### Step 3:
Create tables by running this query

```
CREATE TABLE Address.eth_token_interaction_partitioned
(
  name STRING,
  symbol STRING,
  token_address STRING,
  wallet_address STRING,
  balance FLOAT64,
  last_transacted TIMESTAMP

)
PARTITION BY
  DATE(last_transacted)
```
This table has name starts with eth. This table will be used to store ethereum 
related data, 
For multiple blockchains use different Tables.

### Step 4: 
This is meant for polygon blockchain.
Paste this query in big query editor
replace INterval 60 days with 1 day and check if the results are acceptable.

```
with wallet_balances AS (
      SELECT
        token_address,
        CAST(value AS FLOAT64) AS value,
        block_timestamp,
        to_address AS address
      FROM
        `bigquery-public-data.crypto_polygon.token_transfers`
      WHERE
        DATE(block_timestamp) > DATE_SUB(CURRENT_DATE(), INTERVAL 60 day)
      UNION ALL
      SELECT
        token_address,
        -CAST(value AS FLOAT64) AS value,
        block_timestamp,
        from_address AS address
      FROM
        `bigquery-public-data.crypto_polygon.token_transfers`
    WHERE
      DATE(block_timestamp) > DATE_SUB(CURRENT_DATE(), INTERVAL 60 day)
),

aggregated_wallet_balances AS (
   SELECT
      token_address,
      address,
      MAX(block_timestamp) AS last_transacted,
      SUM(value) AS balance
  from wallet_balances
  where address != "0x0000000000000000000000000000000000000000"
  GROUP BY
      token_address,
      address
),

token_address_with_name AS (
    SELECT
    tokens.name,
    tokens.symbol,
    token_address,
    contracts.address as wallet_address,
    contracts.balance,
    contracts.last_transacted
    FROM
    aggregated_wallet_balances as contracts
    LEFT JOIN
    `pingboxproduction.Address.coingecko-token-list2` AS tokens
    ON
    (contracts.token_address = tokens.polygon)
)

select * from token_address_with_name

```
For the first time, Click on MOre and query settings. 
Save the data on the table created in the previous step.



### Step 5: 
Click on this same query, an click on Schedule Query.
Fill up the details for the table created at step 3.

## ----------------------------------- Purpose -------------------------------------------


- All 25 smart contract addresses on Ethereum and polygon, in a category (NFT, Gaming, DEFI)

- ON a smart contract
    - All addresses with their holdings
    - All addresses with their last active time so filtering on the timestamp
    - All addresses with most number of transactions 


- Get All adddresses with their holdings on a particular smnart contract (NFT project also)
- Get All addresses with their holdings on two or more smart contracts (NFT projects also)



## -------------------------------  Miscelleneous  -------------------------------------

### All the contract addresses are present in contracts table. They are really accurate.

### How to check if uniswap exists in the table

Uniswapo was deployed 739 days ago , Todays date is 15/09/2022
Block: 10861674 4676436 Block Confirmations
Timestamp: 730 days 14 hrs ago (Sep-14-2020 06:11:26 PM +UTC)

```
SELECT * FROM `bigquery-public-data.crypto_ethereum.contracts` 
WHERE address = "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984"
and DATE(block_timestamp) BETWEEN 
DATE_SUB(CURRENT_DATE(), INTERVAL 750 day)
and DATE_SUB(CURRENT_DATE(), INTERVAL 700 day)
```


### TOKEN_TRANSFERS table has all the contract addresses and their transfers

Here is an example that shows all the transfers happend on Uniswap contract address
between two timestamps.
```
SELECT * FROM `bigquery-public-data.crypto_ethereum.token_transfers` 
WHERE token_address = "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984"
and DATE(block_timestamp) BETWEEN 
DATE_SUB(CURRENT_DATE(), INTERVAL 20 day)
and DATE_SUB(CURRENT_DATE(), INTERVAL 10 day)
```


