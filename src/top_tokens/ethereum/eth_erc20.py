
from top_tokens.utils import run_graphql_query
from utils.errors import CustomError

async def eth_erc20_1day( skip, limit):
    url = "https://api.zettablock.com/api/v1/dataset/sq_84eaf24c3dcc45129b12a194e792f8f6/graphql"
    oldurl = "https://api.zettablock.com/api/v1/dataset/sq_d6ef18d1cd44404ba31eac832b34a94d/graphql"
    query = """{
        records(limit:%s, skip: %s 
    	orderBy: total_transactions, orderDirection: desc
        ){
            total_transactions
            name
            contract_address
            }
            }
        """%(limit, skip)
    return await run_graphql_query(url, query)

async def eth_erc20_3day( skip, limit):
    url = "https://api.zettablock.com/api/v1/dataset/sq_e75311701f57472da518c008393b52ee/graphql"
    oldurl = "https://api.zettablock.com/api/v1/dataset/sq_dea49f41bea44ff9bc86d2d6124e3f02/graphql"
    query = """{
        records(limit:%s, skip: %s 
    	orderBy: total_transactions, orderDirection: desc
        ){
            total_transactions
            name
            contract_address
            }
            }
        """%(limit, skip)
    return await run_graphql_query(url, query)



async def eth_erc20_7day(skip, limit):
    url = "https://api.zettablock.com/api/v1/dataset/sq_0e43d32e1c0642eaa8b661d434af5a0c/graphql"
    oldurl ="https://api.zettablock.com/api/v1/dataset/sq_a88a25f4ea464306b080cbe545223ba0/graphql"
    query = """{
        records(limit:%s, skip: %s 
    	orderBy: total_transactions, orderDirection: desc
        ){
            total_transactions
            name
            contract_address
            }
            }
        """%(limit, skip)
    return await run_graphql_query(url, query)




async def eth_erc20_15day(skip, limit):
    url = "https://api.zettablock.com/api/v1/dataset/sq_d8c9e4fd5b1d4f7fb305f723a6285215/graphql"
    oldurl = "https://api.zettablock.com/api/v1/dataset/sq_db7bc78211ed4863a30fef16429544c7/graphql"
    query = """{
        records(limit:%s, skip: %s 
    	orderBy: total_transactions, orderDirection: desc
        ){
            total_transactions
            name
            contract_address
            }
            }
        """%(limit, skip)
    return await run_graphql_query(url, query)

async def eth_erc20_top_tokens(days, skip, limit):
    if int(days) == 1:
        return await eth_erc20_1day(skip, limit)

    elif int(days) == 3:
        return await eth_erc20_3day(skip, limit)

    elif int(days) == 7:
        return await eth_erc20_7day(skip, limit)

    elif int(days) == 15:
        return await eth_erc20_15day(skip, limit)
    else:
        raise CustomError("days not supported yet")