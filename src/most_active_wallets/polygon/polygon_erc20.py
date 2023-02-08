
from most_active_wallets.utils import run_graphql_query
from utils.errors import CustomError

async def polygon_erc20_1day( skip, limit):
    url="https://api.zettablock.com/api/v1/dataset/sq_0399e032e3aa4e7691df339daba79b2e/graphql"
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

async def polygon_erc20_7day(skip, limit):
    url="https://api.zettablock.com/api/v1/dataset/sq_ddec0715ffc748039d21c9aa36ec601e/graphql"
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




async def polygon_erc20_15day(skip, limit):
    url="https://api.zettablock.com/api/v1/dataset/sq_3570d8ce7af446fba3527723e3d613b9/graphql"
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

async def polygon_erc20_top_wallets(days, skip, limit):
    if int(days) == 1:
        return await polygon_erc20_1day(skip, limit)

    elif int(days) == 7:
        return await polygon_erc20_7day(skip, limit)

    elif int(days) == 15:
        return await polygon_erc20_15day(skip, limit)
    else:
        raise CustomError("days not supported yet")