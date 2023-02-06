
import json
from sanic import Blueprint
from utils.utils import Response
from utils.errors import CustomError
from loguru import logger
from .ethereum.eth_erc20 import eth_erc20_top_wallets
from .ethereum.eth_erc721 import eth_erc721_top_wallets
from .ethereum.eth_erc1155 import eth_erc1155_top_wallets
from caching.cache_utils import cache_validity, get_cache, set_cache, delete_cache


ACTIVE_WALLETS_BP = Blueprint("wallets", url_prefix='/wallets', version=1)



def make_query_string(request_args: dict, args_list: list) -> str:
    query_string = ""
    for (key, value) in request_args.items():
        if key in args_list:
            if type(value) == list:
                value = value[0]
            query_string += f"&{key}={value}"
    return query_string[1:]


async def active_wallets_caching(app: object, caching_key: str, caching_ttl:int, request_args: dict) -> any: 
    cache_valid = await cache_validity(app.config.REDIS_CLIENT, caching_key, caching_ttl)

    if not cache_valid:
        data = await get_active_wallets_data(request_args)
        if data: #only set cache when data is not empty
            await set_cache(app.config.REDIS_CLIENT, caching_key, data)
        return data
    result = await get_cache(app.config.REDIS_CLIENT, caching_key)
    return json.loads(result)



async def get_active_wallets_data(request_args):
    logger.info("Error popping up from here")
    logger.info(request_args.get("number_of_days"))
    logger.info(request_args.get("skip"))
    logger.info(request_args.get("limit"))
    
    try:
        if request_args.get("erc_type") == "ERC20":
            result = await eth_erc20_top_wallets(request_args.get("number_of_days"), request_args.get("skip"), request_args.get("limit"))
        elif request_args.get("erc_type") == "ERC721":
            result = await eth_erc721_top_wallets(request_args.get("number_of_days"), request_args.get("skip"),request_args.get("limit"))
        else:
            result = await eth_erc1155_top_wallets(request_args.get("number_of_days"), request_args.get("skip"), request_args.get("limit"))
    except Exception as e:
        raise CustomError(e.__str__())

    return result

@ACTIVE_WALLETS_BP.get('<chain>/most_active')
# @is_subscribed()
async def most_active(request, chain):
    caching_ttl =  request.app.config.CACHING_TTL['LEVEL_FOUR']


    if chain not in request.app.config.SUPPORTED_CHAINS:
        raise CustomError("chain not suported")

    if not request.args.get("erc_type"):
        raise CustomError("ERC Type is required")

    if not request.args.get("erc_type") in ["ERC20", "ERC721", "ERC1155"]:
        raise CustomError("ERC Type is not valid")

    if not request.args.get("number_of_days"):
        request.args["number_of_days"] = [7]
        number_of_days = 7
    else: 
        number_of_days = int(request.args.get("number_of_days"))

    if not request.args.get("limit"):
        request.args["limit"] = [1000]
    
    if not request.args.get("skip"):
        request.args["skip"] = [0]
    

    query_string: str = make_query_string(request.args, ["erc_type", "number_of_days", "limit", "skip"])

    caching_key = f"{request.route.path.replace('<chain:str>', chain)}?{query_string}"

    data = await active_wallets_caching(request.app, caching_key, caching_ttl, request.args)

    return Response.success_response(data=data)