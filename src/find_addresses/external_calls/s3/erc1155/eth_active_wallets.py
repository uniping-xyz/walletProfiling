import os
import boto3


async def erc1155_active_wallets(number_of_days, limit):
    if number_of_days == 1:
        return await erc1155_one_day_active_wallets(limit)
    elif number_of_days == 3:
        return await erc1155_three_day_active_wallets(limit)
    elif number_of_days == 7:
        return await erc1155_seven_day_active_wallets(limit)
    else:
        raise Exception("Number of days not supported")



async def erc1155_one_day_active_wallets(limit):
    file_name = os.environ['ETH_ERC1155_ONE_DAY_FILE_NAME']
    return await fetch_data(file_name, limit)

async def erc1155_three_day_active_wallets(limit):
    file_name = os.environ['ETH_ERC1155_THREE_DAY_FILE_NAME']
    return await fetch_data(file_name, limit)

async def erc1155_seven_day_active_wallets(limit):
    file_name = os.environ['ETH_ERC1155_SEVEN_DAY_FILE_NAME']
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