
from most_active_wallets.utils import run_graphql_query
from utils.errors import CustomError




async def eth_erc721_7day(skip, limit):
    url ="https://api.zettablock.com/api/v1/dataset/sq_7c6f5a10fc6b43dd95f1fc2cabde0580/graphql"
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


async def eth_erc721_1day( skip, limit):
    url = "https://api.zettablock.com/api/v1/dataset/sq_765bf7482d3c4e538ad55434ffc9756b/graphql"
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

async def eth_erc721_15day(skip, limit):
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

async def eth_erc721_top_wallets(days, skip, limit):
    if int(days) == 1:
        return await eth_erc721_1day(skip, limit)

    elif int(days) == 7:
        return await eth_erc721_7day(skip, limit)

    elif int(days) == 15:
        return await eth_erc721_15day(skip, limit)
    else:
        raise CustomError("days not supported yet")