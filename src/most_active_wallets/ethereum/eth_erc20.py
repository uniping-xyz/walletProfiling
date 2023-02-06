
from most_active_wallets.utils import run_graphql_query
from utils.errors import CustomError

async def eth_erc20_1day( skip, limit):
    url = "https://api.zettablock.com/api/v1/dataset/sq_f7279f447ff24055b7bbdaa607045b56/graphql"
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

async def eth_erc20_7day(skip, limit):
    url ="https://api.zettablock.com/api/v1/dataset/sq_77b0fcd69ff440ffa64ed6ab62d75f57/graphql"
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




async def eth_erc20_15day(skip, limit):
    url = "https://api.zettablock.com/api/v1/dataset/sq_d9735c43744d4e62adf292828fa02dcc/graphql"
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

async def eth_erc20_top_wallets(days, skip, limit):
    if int(days) == 1:
        return await eth_erc20_1day(skip, limit)

    elif int(days) == 7:
        return await eth_erc20_7day(skip, limit)

    elif int(days) == 15:
        return await eth_erc20_15day(skip, limit)
    else:
        raise CustomError("days not supported yet")