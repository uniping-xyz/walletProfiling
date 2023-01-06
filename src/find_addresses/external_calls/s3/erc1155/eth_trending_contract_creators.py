


import os
import boto3
from loguru import logger

"""
with contracts as (select block_hash, address from ethereum.contracts
where is_erc20=1
and DATE(block_timestamp) > DATE(now()) - toIntervalDay(120)),


txs as (select block_hash, receipt_contract_address, from_address, block_number, block_timestamp from ethereum.transactions
where  DATE(block_timestamp) > DATE(now()) - toIntervalDay(365)
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
async def erc1155_trending_contract_creators(limit):
    file_name = os.environ['ETH_ERC1155_CONTRACT_CREATORS_FILE_NAME']
    logger.info(f"Fetching data from {file_name}")
    return await fetch_data(file_name, limit)


async def fetch_data(file_name, limit):
    region_name = os.environ["REGION_NAME"]
    aws_access_key_id = os.environ["ACCESS_KEY"]
    aws_secret_access_key = os.environ["SECRET_KEY"]
    s3_client = boto3.client('s3',
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                    region_name=region_name
                    )
    bucket_name = os.environ['DATA_BUCKET_NAME']

    resp = s3_client.select_object_content(
          Bucket=bucket_name,
          Key=file_name,
          ExpressionType='SQL',
          Expression=f"SELECT * FROM s3object limit {limit}",
          InputSerialization = {'CSV': {"FileHeaderInfo": "Use"}, 'CompressionType': 'NONE'},
          OutputSerialization = {'CSV': {}},
      )
    result = []

    if resp.get("Payload"):
        for event in resp['Payload']:
            if 'Records' in event:
                records = event['Records']['Payload'].decode('utf-8').split()
                for e in records:
                    result.append(e.split(","))
        return result

    return []