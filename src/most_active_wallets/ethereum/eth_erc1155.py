
from most_active_wallets.utils import run_graphql_query
from utils.errors import CustomError


async def eth_erc1155_1day( skip, limit):
    url = "https://api.zettablock.com/api/v1/dataset/sq_810f2eaee267486aa0a90eea4d728e99/graphql"
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

async def eth_erc1155_7day(skip, limit):
    url ="https://api.zettablock.com/api/v1/dataset/sq_ea76f6340f0841c9ac4e3bea7ab3f71a/graphql"
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




async def eth_erc1155_15day(skip, limit):
    url = "https://api.zettablock.com/api/v1/dataset/sq_e757a15e0a374bd5ab88332a05801cfa/graphql"
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

async def eth_erc1155_top_wallets(days, skip, limit):
    if int(days) == 1:
        return await eth_erc1155_1day(skip, limit)

    elif int(days) == 7:
        return await eth_erc1155_7day(skip, limit)

    elif int(days) == 15:
        return await eth_erc1155_15day(skip, limit)
    else:
        raise CustomError("days not supported yet")