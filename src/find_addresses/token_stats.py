import requests
import json
import asyncio
import aiohttp
from sanic import Blueprint
from utils.utils import Response
from utils.errors import CustomError
from utils.authorization import is_subscribed
from loguru import logger
from google.cloud import bigquery
from sanic.request import RequestParameters
from caching.cache_utils import cache_validity, get_cache, set_cache, delete_cache

import re
from caching.cache_utils import cache_validity, get_cache, set_cache, delete_cache

TOKEN_STATS_BP = Blueprint("stats", url_prefix='/stats', version=1)


#if the contract is not a token
@TOKEN_STATS_BP.get('contract_stats')
@is_subscribed()
async def contract_stats(request):
 
    raise CustomError("Not implemented yet")


def make_query_string(request_args: dict, args_list: list) -> str:
    query_string = ""
    for (key, value) in request_args.items():
        if key in args_list:
            if type(value) == list:
                value = value[0]
            query_string += f"&{key}={value}"
    return query_string[1:] # to remove the first $ sign appened to the string


"""
with transactions AS (
select *
  from `pingboxproduction.Address.total_transactions_pertoken_perday`
  where token_address = lower("0x7D1AfA7B718fb893dB30A3aBc0Cfc608AaCfeBB0")
),
unique_addresses AS (
  select *
    from `pingboxproduction.Address.unique_addresses_pertoken_perday`
    where token_address = lower("0x7D1AfA7B718fb893dB30A3aBc0Cfc608AaCfeBB0")
)
select transactions.m_block_timestamp as date, transactions.total_transactions, unique_addresses.unique_addresses from
 transactions
JOIN
  unique_addresses 
ON transactions.m_block_timestamp = unique_addresses.m_block_timestamp
ORDER BY
    transactions.m_block_timestamp DESC
"""

@TOKEN_STATS_BP.get('token_stats')
@is_subscribed()
async def token_stats(request):

    if not request.args.get("token_address") :
        raise CustomError("token_address is required ")

    if not request.args.get("chain") or  request.args.get("chain") not in ["ethereum", "polygon"]:
        raise CustomError("Chain is required and should be either ethereum or polygon")
    
    token_address = request.args.get("token_address")
    
    
    query_string: str = make_query_string(request.args, ["chain", "token_address"])
    if request.app.config.CACHING:
        caching_key = f"{request.route.path}?{query_string}"
        logger.info(f"Here is the caching key {caching_key}")
        data = await token_stats_caching(request.app, caching_key, request.args)
    else:
        data = await fetch_token_stats(request.app, request.args)
       
    # logger.success(result)
    # logger.success(f"Length of the result returned is {len(result)}")
    return Response.success_response(data=data)



async def token_stats_caching(app: object, caching_key: str, request_args: dict) -> any: 
    cache_valid = await cache_validity(app.config.REDIS_CLIENT, caching_key, 
                            app.config.CACHING_TTL['LEVEL_FIVE'])

    if not cache_valid:
        data = await fetch_token_stats(app, request_args)
        if data: #only set cache when data is not empty
            await set_cache(app.config.REDIS_CLIENT, caching_key, data)
        return data
    result= await get_cache(app.config.REDIS_CLIENT, caching_key)
    return json.loads(result)

async def fetch_token_stats(app: object, request_args: RequestParameters) -> list:
    query = f"""
                with transactions AS (
                    select *
                        from `pingboxproduction.Address.total_transactions_pertoken_perday`
                        where token_address = lower("{request_args.get('token_address')}")
                    ),
                unique_addresses AS (
                    select *
                        from `pingboxproduction.Address.unique_addresses_pertoken_perday`
                        where token_address = lower("{request_args.get('token_address')}")
                    )
                
                select transactions.m_block_timestamp as date, 
                    transactions.total_transactions, 
                    unique_addresses.unique_addresses 
                from
                    transactions
                JOIN
                    unique_addresses 
                ON transactions.m_block_timestamp = unique_addresses.m_block_timestamp
                ORDER BY
                transactions.m_block_timestamp DESC
    """
    client = bigquery.Client()
    results = client.query(query)
    if results:
        result = []
        for row in results.result():
            result.append({
                    "total_transactions": row['total_transactions'],
                    "timestamp": row['date'].strftime("%s"),
                    "unique_addresses": row["unique_addresses"]
                    # "name": name,
                    # "symbol": symbol
            }) 
        return result
    logger.error(f"No data returned from google biq uery for TokenAddress=[{request_args.get('token_address')}]")
    return []

@TOKEN_STATS_BP.get('token_stats_average')
@is_subscribed()
async def token_stats_average(request):
    if not request.args.get("token_address") :
        raise CustomError("token_address is required ")

    if not request.args.get("chain") or  request.args.get("chain") not in ["ethereum", "polygon"]:
        raise CustomError("Chain is required and should be either ethereum or polygon")
    url = f"https://api.coingecko.com/api/v3/nfts/{request.args.get('chain')}/contract/{request.args.get('token_address')}"
    logger.success(url)
    r = requests.get(url)
    result = r.json()

    logger.success(result)
    logger.success(f"Length of the result returned is {len(result)}")
    return Response.success_response(data=result)
