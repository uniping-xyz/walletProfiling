
from most_active_wallets.utils import run_graphql_query
from utils.errors import CustomError


async def polygon_erc1155_1day( skip, limit):
    url = "https://api.zettablock.com/api/v1/dataset/sq_86915b0ec44a423e86c075a060a1fed6/graphql"
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

async def polygon_erc1155_7day(skip, limit):
    url="https://api.zettablock.com/api/v1/dataset/sq_5686035eb35d4b799f6a07a08defe6c7/graphql"
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




async def polygon_erc1155_15day(skip, limit):
    url="https://api.zettablock.com/api/v1/dataset/sq_5bca20619cbd4f3fa9165032bbaed62f/graphql"
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

async def polygon_erc1155_top_wallets(days, skip, limit):
    if int(days) == 1:
        return await polygon_erc1155_1day(skip, limit)

    elif int(days) == 7:
        return await polygon_erc1155_7day(skip, limit)

    elif int(days) == 15:
        return await polygon_erc1155_15day(skip, limit)
    else:
        raise CustomError("days not supported yet")