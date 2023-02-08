
from most_active_wallets.utils import run_graphql_query
from utils.errors import CustomError

async def polygon_erc721_1day( skip, limit):
    url ="https://api.zettablock.com/api/v1/dataset/sq_8724ab72879147a3be83f0b606fc7304/graphql"
    query = """{
        records(limit:%s, skip: %s 
    	orderBy: total_transactions, orderDirection: desc
        ){
            total_transactions
            wallet_address
            }
            }
        """%(limit, skip)
    return await run_graphql_query(url, query)



async def polygon_erc721_7day(skip, limit):
    url = "https://api.zettablock.com/api/v1/dataset/sq_8651ddd85633459ba8a9de15cc50f210/graphql"
    query = """{
        records(limit:%s, skip: %s 
    	orderBy: total_transactions, orderDirection: desc
        ){
            total_transactions
            wallet_address
            }
            }
        """%(limit, skip)
    return await run_graphql_query(url, query)



async def polygon_erc721_15day(skip, limit):
    url ="https://api.zettablock.com/api/v1/dataset/sq_ed17240949e14c0d87ef6afc0922e9c1/graphql"
    query = """{
        records(limit:%s, skip: %s 
    	orderBy: total_transactions, orderDirection: desc
        ){
            total_transactions
            wallet_address
            }
            }
        """%(limit, skip)
    return await run_graphql_query(url, query)

async def polygon_erc721_top_wallets(days, skip, limit):
    if int(days) == 1:
        return await polygon_erc721_1day(skip, limit)

    elif int(days) == 7:
        return await polygon_erc721_7day(skip, limit)

    elif int(days) == 15:
        return await polygon_erc721_15day(skip, limit)
    else:
        raise CustomError("days not supported yet")