from symtable import Symbol
from sanic import Blueprint
import datetime
from loguru import logger
import requests
from utils.utils import Response
from utils.authorization import authorized, authorized_optional
from utils.errors import CustomError
from .utils import get_tagged_ethereum_contracts
import datetime
import json
import aiohttp
from google.cloud import bigquery
import re

FIND_ADDRESSES_BP = Blueprint("channels", url_prefix='/find_address', version=1)



"""
    SELECT wallet_address, Max(last_transacted) as last_transacted, count(*) AS c
            FROM `pingboxproduction.Address.eth_token_interaction_partitioned`
            WHERE  token_address = "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984" or token_address='0x6b3595068778dd592e39a122f4f5a5cf09c90fe2' or token_address = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
               AND  last_transacted  BETWEEN "2022-09-15" and "2022-09-18" 
            group by wallet_address
            having c = 3


"""

@FIND_ADDRESSES_BP.get('token_data')
#@authorized
async def token_data(request):
    #amafans_channel_object = request.app.config.amafans_channel_object
    if not request.args.get("limit"):
        limit = 100
    else:
        limit =  request.args.get("limit")

    if not request.args.get("offset"):
        offset = 0
    else:
        offset = request.args.get("offset")



    if not request.args.get("token_addresses") :
        raise CustomError("token_addresses is required ")

    if not request.args.get("chain") or  request.args.get("chain") not in ["ethereum", "polygon"]:
        raise CustomError("Chain is required and should be either ethereum or polygon")

    if request.args.get("chain") ==  "polygon":
        query = f"""
            SELECT wallet_address, balance, Max(last_transacted) as last_transacted, count(*) AS c
            FROM `{request.app.config.bq_polygon_table}`
            """        
    else:
        query = f"""
            SELECT wallet_address, balance, Max(last_transacted) as last_transacted, count(*) AS c
            FROM `{request.app.config.bq_eth_table}`
            """

    token_addresses = [addr.replace(" ", "") for addr in request.args.get("token_addresses").split(",")]

    and_statement = ""
    for (index, token_address) in enumerate(token_addresses):
        _token_address = token_address.lower()
        if index == 0:
            and_statement += f"WHERE token_address='{_token_address}' "
        else:
            and_statement += f"OR token_address='{_token_address}' "

    query += and_statement
    if not request.args.get("from_date") or not request.args.get("to_date"):
        raise CustomError("from_date and to_date params are required")
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')

    if from_date > to_date:
        raise CustomError("Invalid date range")

    datetime.datetime.strptime(from_date,"%Y-%m-%d")
    datetime.datetime.strptime(to_date,"%Y-%m-%d")

    query +=  f"""AND last_transacted  
                BETWEEN '{from_date}' and '{to_date}'
                """

    query += f""" group by wallet_address, balance
                having c = {len(token_addresses)}
                order by balance desc
                LIMIT {limit}
                OFFSET {offset}"""
    
    # # _query = json.dumps(query)
    print (query)

    client = bigquery.Client()
    results = client.query(query)
    result = []
    for row in results.result():
        # if request.args.get("chain") ==  "ethereum":
        #     document = await request.app.config.TOKENS.find_one({"ethereum": row['token_address']})
        # else:
        #     document = await request.app.config.TOKENS.find_one({"polygon": row['token_address']})
        # if document:
        #     name = document.get("name")
        #     symbol = document.get("symbol")
        # else:
        #     name = row["name"]
        #     symbol = row["symbol"]
        result.append({
                "wallet_address": row['wallet_address'],
                "last_transacted": row['last_transacted'].strftime("%s"),
                # "name": name,
                # "symbol": symbol
        })
    logger.success(f"Length of the result returned is {len(result)}")
    await request.app.config.QUERIES.insert_one({"query": query, "result_length": len(result), "result": result })
    sorted_result = sorted(result,  key=lambda d: d['last_transacted'], reverse=True
    )
    return Response.success_response(data=sorted_result)


@FIND_ADDRESSES_BP.get('wallet_data')
#@authorized
async def token_data(request):
    #amafans_channel_object = request.app.config.amafans_channel_object
    wallet_address = request.args.get('wallet_address')
    if not request.args.get("wallet_address") :
        raise CustomError("wallet_address  is required")

    if not request.args.get("chain") or  request.args.get("chain") not in ["ethereum", "polygon"]:
        raise CustomError("Chain is required and should be either ethereum or polygon")

    if request.args.get("chain") ==  "polygon":
        query = f"""
            SELECT *
            FROM `{request.app.config.bq_polygon_table}`
            """        
    else:
        query = f"""
            SELECT *
            FROM `{request.app.config.bq_eth_table}`
            """


    and_statement = f'WHERE wallet_address="{wallet_address}" '

    query += and_statement
    client = bigquery.Client()
    print (query)

    return Response.success_response(data=query)



@FIND_ADDRESSES_BP.get('user_token_balances')
async def user_token_balances(request):
    wallet_address = request.args.get('wallet_address')
    if not wallet_address:
        raise CustomError("Wallet address is required")
    headers = {'Content-type': 'application/json'}
    params = {"jsonrpc":"2.0","method":"alchemy_getTokenBalances","params": [request.args.get('wallet_address').lower(), "erc20"],"id":"42"}
    async with aiohttp.ClientSession() as session:
        async with session.post(request.app.config.WEB3_PROVIDER, json=params, headers=headers) as resp:
            response  = await resp.json()
    logger.success(response)
    result = []
    for e in response["result"]["tokenBalances"]:
        contract_address = e["contractAddress"]
        token_balance = e["tokenBalance"]
        _contract_address =  await request.app.config.TOKENS.find_one({"ethereum": contract_address.lower()}, 
                        projection={"ethereum":  True, "name": True})
        if _contract_address:
            contract_address = _contract_address.get("name")
        balance = int(token_balance.replace("0x", ""), 16)/10**18
        if not round(balance, 2) <= 0.0:
            result.append({"contract_address": contract_address, "balance": balance})
    return Response.success_response(data=result)

@FIND_ADDRESSES_BP.get('find_tags')
async def user_token_balances(request):

    if  request.args.get("chain") not in request.app.config.SUPPORTED_CHAINS:
        raise CustomError("chain not suported")

    if  request.args.get("query"):
        query = f".*{request.args.get('query')}"
    else:
        query = f".*"

    r = re.compile(query)
    result = list(filter(r.match, request.app.config.tags[request.args.get("chain")])) # Read Note below
    return Response.success_response(data=result)


@FIND_ADDRESSES_BP.get('find_tagged_contracts')
async def find_tagged_contracts(request):

    if  request.args.get("chain") not in request.app.config.SUPPORTED_CHAINS:
        raise CustomError("chain not suported")

    if  not request.args.get("tag"):
        raise CustomError("Tag is required")

    result = await get_tagged_ethereum_contracts(request.app.config.LUABASE_API_KEY, request.args.get("tag"))
    return Response.success_response(data=result)



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

@FIND_ADDRESSES_BP.get('token_stats')
#@authorized
async def token_stats(request):

    if not request.args.get("token_address") :
        raise CustomError("token_address is required ")

    if not request.args.get("chain") or  request.args.get("chain") not in ["ethereum", "polygon"]:
        raise CustomError("Chain is required and should be either ethereum or polygon")
    
    token_address = request.args.get("token_address")
    query = f"""
                with transactions AS (
                    select *
                        from `pingboxproduction.Address.total_transactions_pertoken_perday`
                        where token_address = lower("{token_address}")
                    ),

                unique_addresses AS (
                    select *
                        from `pingboxproduction.Address.unique_addresses_pertoken_perday`
                        where token_address = lower("{token_address}")
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
    
    # # _query = json.dumps(query)
    print (query)

    client = bigquery.Client()
    results = client.query(query)
    result = []
    for row in results.result():
        result.append({
                "total_transactions": row['total_transactions'],
                "timestamp": row['date'].strftime("%s"),
                "unique_addresses": row["unique_addresses"]
                # "name": name,
                # "symbol": symbol
        })    
    logger.success(result)
    logger.success(f"Length of the result returned is {len(result)}")
    return Response.success_response(data=result)

