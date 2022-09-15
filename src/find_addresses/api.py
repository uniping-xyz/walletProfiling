from sanic import Blueprint
import datetime
from loguru import logger
import requests
from utils.utils import Response
from utils.authorization import authorized, authorized_optional
from utils.errors import CustomError

FIND_ADDRESSES_BP = Blueprint("channels", url_prefix='/find_address', version=1)


@FIND_ADDRESSES_BP.get('search_token')
#@authorized
async def search_token(request):
    #amafans_channel_object = request.app.config.amafans_channel_object
    
    if not request.args.get("token_name"):
        raise CustomError("token_name is required")

    if not request.args.get("chain") or  request.args.get("chain") not in ["ethereum", "polygon"]:
        raise CustomError("Chain is required and should be either ethereum or polygon")

    query = {request.args.get("chain"): {"$exists": True},
                            "tokens": {"$in": [request.args.get("token_name").lower()] }}
    print (query)

    cursor = request.app.config.TOKENS.find(query, projection={"_id": False, "tokens": False})
    tokens = []
    
    async for document in cursor.limit(5):
        tokens.append(document)

    return Response.success_response(data=tokens)