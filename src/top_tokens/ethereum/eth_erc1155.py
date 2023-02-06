
from top_tokens.utils import run_graphql_query
from utils.errors import CustomError


async def eth_erc1155_1day( skip, limit):
    url = "https://api.zettablock.com/api/v1/dataset/sq_dc95f2da7096487386ef81a9eba6e675/graphql"
    oldurl = "https://api.zettablock.com/api/v1/dataset/sq_fb6424ed866d4a91858c026853c93551/graphql"
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


async def eth_erc1155_7day(skip, limit):
    url = "https://api.zettablock.com/api/v1/dataset/sq_8673abf29bd8413a9602eeb3ea48747b/graphql"
    oldurl ="https://api.zettablock.com/api/v1/dataset/sq_253507b2fe2744678705ea77f08f4ace/graphql"
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




async def eth_erc1155_15day(skip, limit):
    url ="https://api.zettablock.com/api/v1/dataset/sq_422ae71f5a8f4b1ebb89513efb1dfb56/graphql"
    oldurl = "https://api.zettablock.com/api/v1/dataset/sq_9eb60d6823ae4b69b72d51d4bcd09093/graphql"
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

async def eth_erc1155_top_tokens(days, skip, limit):
    if int(days) == 1:
        return await eth_erc1155_1day(skip, limit)
    

    elif int(days) == 7:
        return await eth_erc1155_7day( skip, limit)

    elif int(days) == 15:
        return await eth_erc1155_15day( skip, limit)
    else:
        raise CustomError("days not supported yet")