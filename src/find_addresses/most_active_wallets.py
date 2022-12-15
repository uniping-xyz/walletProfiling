
import json
from sanic import Blueprint
from utils.utils import Response
from utils.errors import CustomError
from utils.authorization import is_subscribed
from loguru import logger
from find_addresses.external_calls.s3.erc20.eth_active_wallets import erc20_active_wallets
from find_addresses.external_calls import luabase_contract_search

ACTIVE_WALLETS_BP = Blueprint("wallets", url_prefix='/wallets', version=1)

@ACTIVE_WALLETS_BP.get('most_active')
# @is_subscribed()
async def most_active(request):
    if request.args.get("chain") not in request.app.config.SUPPORTED_CHAINS:
        raise CustomError("chain not suported")

    if not request.args.get("erc_type"):
        raise CustomError("ERC Type is required")

    if not request.args.get("erc_type") in ["ERC20", "ERC721", "ERC1155"]:
        raise CustomError("ERC Type is not valid")

    if not request.args.get("number_of_days"):
        number_of_days = 3
    else: 
        number_of_days = int(request.args.get("number_of_days"))

    if not request.args.get("limit"):
        request.args["limit"] = [1000]
    

    if request.args.get("erc_type") == "ERC20":
        result = await erc20_active_wallets(number_of_days, request.args.get("limit"))

    return Response.success_response(data=result)