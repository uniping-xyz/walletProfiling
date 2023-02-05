
from top_tokens.utils import run_graphql_query
from utils.errors import CustomError


async def eth_erc721_1day( skip, limit):
    url = "https://api.zettablock.com/api/v1/dataset/sq_6c74f8cde80341a785813761d80ec0f4/graphql"
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


async def eth_erc721_3day( skip, limit):
    url = "https://api.zettablock.com/api/v1/dataset/sq_ad434a928ff94f7dbf4313fd2c3a79c7/graphql"
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



async def eth_erc721_7day(skip, limit):
    url ="https://api.zettablock.com/api/v1/dataset/sq_8360bf52c8d84a3dae4097fa9157265a/graphql"
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




async def eth_erc721_15day(skip, limit):
    url = "https://api.zettablock.com/api/v1/dataset/sq_6c27410b5a834e48a64aa51c1a4fea7f/graphql"
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

async def eth_erc721_top_tokens(days, skip, limit):
    if int(days) == 1:
        return await eth_erc721_1day(skip, limit)

    elif int(days) == 3:
        return await eth_erc721_3day(skip, limit)

    elif int(days) == 7:
        return await eth_erc721_7day(skip, limit)

    elif int(days) == 15:
        return await eth_erc721_15day(skip, limit)
    else:
        raise CustomError("days not supported yet")