
from most_active_wallets.utils import run_graphql_query
from utils.errors import CustomError

async def eth_erc721_1day( skip, limit):
    url = "https://api.zettablock.com/api/v1/dataset/sq_cd942bd9f57b4bcd90a2c8cace5d38bc/graphql" #token_two
    # url ="https://api.zettablock.com/api/v1/dataset/sq_282640124aed4dbdb2b785d12b06ece5/graphql"
    # oldurl = "https://api.zettablock.com/api/v1/dataset/sq_765bf7482d3c4e538ad55434ffc9756b/graphql"
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


async def eth_erc721_3day(skip, limit):
    url = "https://api.zettablock.com/api/v1/dataset/sq_91b8caad34cc43539cb7dc6a8b9fa52f/graphql" #new_token

    # url = "https://api.zettablock.com/api/v1/dataset/sq_cf4d28805c494a69a648ba93419bb195/graphql"
    # oldurl ="https://api.zettablock.com/api/v1/dataset/sq_7c6f5a10fc6b43dd95f1fc2cabde0580/graphql"
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


async def eth_erc721_7day(skip, limit):
    url = "https://api.zettablock.com/api/v1/dataset/sq_33ea479516fb4ca08a0061a13acfe4ed/graphql" #new_token
    # url = "https://api.zettablock.com/api/v1/dataset/sq_cf4d28805c494a69a648ba93419bb195/graphql"
    # oldurl ="https://api.zettablock.com/api/v1/dataset/sq_7c6f5a10fc6b43dd95f1fc2cabde0580/graphql"
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



# async def eth_erc721_15day(skip, limit):
#     url ="https://api.zettablock.com/api/v1/dataset/sq_1bd0e6e2bf4b4fb39ce2638777d921be/graphql"
#     oldurl = "https://api.zettablock.com/api/v1/dataset/sq_d9735c43744d4e62adf292828fa02dcc/graphql"
#     query = """{
#         records(limit:%s, skip: %s 
#     	orderBy: total_transactions, orderDirection: desc
#         ){
#             total_transactions
#             wallet_address
#             }
#             }
#         """%(limit, skip)
#     return await run_graphql_query(url, query)

async def eth_erc721_top_wallets(days, skip, limit):
    if int(days) == 1:
        return await eth_erc721_1day(skip, limit)

    elif int(days) == 3:
        return await eth_erc721_3day(skip, limit)

    elif int(days) == 7:
        return await eth_erc721_7day(skip, limit)

    else:
        raise CustomError("days not supported yet")