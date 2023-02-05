
import aiohttp
from loguru import logger
import os

async def run_graphql_query(url, query):
    logger.info(url)
    logger.info(query)
    headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "X-API-KEY": os.getenv("ZETTABLOCK_API_KEY_ONE")
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
                        url, 
                        json={'query': query},
                        headers = headers ) as response:
            if response.status == 200:
                result = await response.json(content_type=None)
                if result.get('errors'):
                    logger.error('Error running graphql query')
                    logger.error(result['errors'])
                    result['data'] = {}
                    result['data']['records'] = []
                return result['data']['records']
            else:
                raise Exception('Query failed. return code is {}.{}'.format(response.status, query))