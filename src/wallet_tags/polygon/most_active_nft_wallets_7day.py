

from wallet_tags.utils import run_graphql_query

async def polygon_erc721_7day():
    url ="https://api.zettablock.com/api/v1/dataset/sq_64e2107bb62347edb4ad6d818649e0c7/graphql"
    query = """{
        records(
    	orderBy: total_transactions, orderDirection: desc
        ){
            total_transactions
            wallet_address
            }
            }
        """
    return await run_graphql_query(url, query)


