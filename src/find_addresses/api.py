from symtable import Symbol
from sanic import Blueprint
import datetime
from loguru import logger
import requests
from utils.utils import Response
from utils.authorization import authorized, authorized_optional
from utils.errors import CustomError
import datetime
import json
from google.cloud import bigquery

FIND_ADDRESSES_BP = Blueprint("channels", url_prefix='/find_address', version=1)

@FIND_ADDRESSES_BP.get('top_50')
#@authorized
async def search_token(request):
    #amafans_channel_object = request.app.config.amafans_channel_object

    if not request.args.get("days"):
        days = 2
    else:
        days = request.args.get("days")
    if not request.args.get("chain") or  request.args.get("chain") not in ["ethereum", "polygon"]:
        raise CustomError("Chain is required and should be either ethereum or polygon")

    print (request.args.get("chain"))
    if  request.args.get("chain") ==  "ethereum":
        query = f""" With top_50 as (SELECT token_address, count(wallet_address) as tx_count
                     FROM `pingboxproduction.Address.eth_token_interaction_partitioned`
                     WHERE
                     DATE(last_transacted) > DATE_SUB(CURRENT_DATE(), INTERVAL {days} day)
                     Group BY token_address
                     ORDER BY tx_count DESC
                     LIMIT 50)

         select * from top_50
         LEFT JOIN
           `pingboxproduction.Address.coingecko-token-list2` AS tokens
         ON
           (top_50.token_address = tokens.ethereum)
         """
    else:
        query = f""" With top_50 as (SELECT token_address, count(wallet_address) as tx_count
                     FROM `pingboxproduction.Address.polygon_token_interaction_partitioned`
                     WHERE
                     DATE(last_transacted) > DATE_SUB(CURRENT_DATE(), INTERVAL {days} day)
                     Group BY token_address
                     ORDER BY tx_count DESC
                     LIMIT 50)

         select * from top_50
         LEFT JOIN
           `pingboxproduction.Address.coingecko-token-list2` AS tokens
         ON
           (top_50.token_address = tokens.polygon)
         """
    print (query)
    result = []
    client = bigquery.Client()
    _queryResult = client.query(query)
    print (_queryResult.result())
    for row in _queryResult.result():
        if request.args.get("chain") ==  "ethereum":
            document = await request.app.config.TOKENS.find_one({"ethereum": row['token_address']})
        else:
            document = await request.app.config.TOKENS.find_one({"polygon": row['token_address']})
        if document:
            name = document.get("name")
            symbol = document.get("symbol")
        else:
            name = row["name"]
            symbol = row["symbol"]
        result.append({"token_address": row['token_address'],
                "tx_count": row['tx_count'],
                "name": name,
                "symbol": symbol
        })
     
    return Response.success_response(data=result)


@FIND_ADDRESSES_BP.get('search_token')
#@authorized
async def search_token(request):
    #amafans_channel_object = request.app.config.amafans_channel_object
    
    if not request.args.get("token_name"):
        raise CustomError("token_name is required")

    if not request.args.get("chain") or  request.args.get("chain") not in ["ethereum", "polygon"]:
        raise CustomError("Chain is required and should be either ethereum or polygon")

    query = {request.args.get("chain"): {"$ne": None},
                            "tokens": {"$in": [request.args.get("token_name").lower()] }}
    print (query)

    cursor = request.app.config.TOKENS.find(query, projection={"_id": False, "tokens": False})
    tokens = []
    
    async for document in cursor.limit(5):
        tokens.append(document)

    return Response.success_response(data=tokens)


@FIND_ADDRESSES_BP.get('token_data')
#@authorized
async def token_data(request):
    #amafans_channel_object = request.app.config.amafans_channel_object
    
    if not request.args.getlist("token_addresses") :
        raise CustomError("token_addresses is required and must be List")

    if type(request.args.getlist("token_addresses")) != list:
        raise CustomError("token_addresses is required and must be List")

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


    and_statement = ""
    for (index, token_address) in enumerate(request.args.getlist("token_addresses")):
        _token_address = token_address.lower()
        if index == 0:
            and_statement += f"WHERE token_address='{_token_address}' "
        else:
            and_statement += f"AND token_address='{_token_address}' "

    query += and_statement
    if request.args.get("last_active"):
        last_transacted = request.args.get('last_transacted')
        
        datetime.datetime.strptime(last_transacted,"%Y-%m-%d")
        # except ValueError as err:
        #     raise CustomError("Invalid date format , must be in `%Y-%m-%d`")

        query +=  f'AND  DATE(last_transacted) > "{last_transacted}"'


    # query = """
    #     SELECT corpus AS title, COUNT(word) AS unique_words
    #     FROM `bigquery-public-data.samples.shakespeare`
    #     GROUP BY title
    #     ORDER BY unique_words
    #     DESC LIMIT 10
    # """

    query += " ORDER BY last_transacted"
    
    # _query = json.dumps(query)
    
    client = bigquery.Client()
    results = client.query(query)
    result = []
    for row in results.result():
        if request.args.get("chain") ==  "ethereum":
            document = await request.app.config.TOKENS.find_one({"ethereum": row['token_address']})
        else:
            document = await request.app.config.TOKENS.find_one({"polygon": row['token_address']})
        if document:
            name = document.get("name")
            symbol = document.get("symbol")
        else:
            name = row["name"]
            symbol = row["symbol"]
        result.append({"token_address": row['token_address'],
                "wallet_address": row['wallet_address'],
                "last_transacted": row['last_transacted'].strftime("%s"),
                "name": name,
                "symbol": symbol
        })

    return Response.success_response(data=result)


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

