


from utils.errors import CustomError
import os
import aiohttp

async def get_nft_collections(params):
    headers = {'X-API-Key': os.environ["BLOCK_DAEMON_SECRET"] }
    async with aiohttp.ClientSession() as session:
        async with session.get("https://svc.blockdaemon.com/nft/v1/ethereum/mainnet/collections", params=params, headers=headers) as resp:
            response  = await resp.json()
    return response

# async def nft_metadata_blockdaemon(app):


# async def token_stats_average(request):
#     if not request.args.get("token_address") :
#     #     https://svc.blockdaemon.com/nft/v1/ethereum/mainnet/collection?contract_address=0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D
#         raise CustomError("token_address is required ")

#     if not request.args.get("chain") or  request.args.get("chain") not in request.app.SUPPORTED:
#         raise CustomError("Chain is required and should be either ethereum or polygon")
#     url = f"https://api.coingecko.com/api/v3/nfts/{request.args.get('chain')}/contract/{request.args.get('token_address')}"
#     logger.success(url)
#     r = requests.get(url)
#     result = r.json()

#     logger.success(result)
#     logger.success(f"Length of the result returned is {len(result)}")
#     return Response.success_response(data=result)
