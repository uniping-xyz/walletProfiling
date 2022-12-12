import json
from loguru import logger
from sanic import Blueprint
from utils.utils import Response
from utils.errors import CustomError
from sanic.request import RequestParameters
from utils.authorization import is_subscribed
from caching.cache_utils import cache_validity, get_cache, set_cache, delete_cache
from find_addresses.external_calls import luabase_token_holders
TOKEN_HOLDERS_BP = Blueprint("holders", url_prefix='/holders/', version=1)



def make_query_string(request_args: dict) -> str:
    query_string = ""
    for (key, value) in request_args.items():
        if type(value) == list:
            value = value[0]
        query_string += f"&{key}={value}"
    return query_string[1:] # to remove the first $ sign appened to the string

@TOKEN_HOLDERS_BP.get('tokens')
@is_subscribed()
async def token_holders(request):
    if request.args.get("chain") not in request.app.config.SUPPORTED_CHAINS:
        raise CustomError("chain not suported")

    if not request.args.get("erc_type"):
        raise CustomError("ERC Type is required")

    if not request.args.get("contract_address"):
        raise CustomError("contract_address is required")

    if not request.args.get("erc_type") in ["ERC20", "ERC721", "ERC1155"]:
        raise CustomError("ERC Type is not valid")

    if not request.args.get("limit"):
        request.args["limit"] = [20]

    if not request.args.get("offset"):
        request.args["offset"] = [0]

    query_string: str = make_query_string(request.args)
    if request.app.config.CACHING:
        caching_key = f"{request.route.path}?{query_string}"
        logger.info(f"Here is the caching key {caching_key}")
        data = await token_holders_caching(request.app, caching_key, request.args)
    else:
        data = await fetch_data(request.app, request.args)
    result = []
    for row in data:
        result.append({
                "balance": row['balance'],
                "address": row['address'],
        })
    logger.success(f"Length of the result returned is {len(result)}")
    return Response.success_response(data=result)

async def token_holders_caching(app: object, caching_key: str, request_args: dict) -> any: 
    cache_valid = await cache_validity(app.config.REDIS_CLIENT, caching_key, 
                            app.config.CACHING_TTL['LEVEL_FIVE'])

    if not cache_valid:
        data = await fetch_data(app, request_args)
        await set_cache(app.config.REDIS_CLIENT, caching_key, data)
        return data
    result= await get_cache(app.config.REDIS_CLIENT, caching_key)
    return json.loads(result)

async def fetch_data(app: object, request_args: RequestParameters) -> any:

    if request_args.get("erc_type") ==  "ERC20":
        results = await luabase_token_holders.holders_ERC20(  
                    request_args.get("contract_address"),  request_args.get("limit"),  
                    request_args.get("offset"))

    elif request_args.get("erc_type") ==  "ERC721":
        results = await luabase_token_holders.holders_ERC721(
                    request_args.get("contract_address"),  request_args.get("limit"),  
                    request_args.get("offset"))    
    else:
        results = await luabase_token_holders.holders_ERC1155(
                    request_args.get("contract_address"),  request_args.get("limit"),  
                    request_args.get("offset"))
    return results









