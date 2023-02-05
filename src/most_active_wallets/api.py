
import json
from sanic import Blueprint
from utils.utils import Response
from utils.errors import CustomError
from loguru import logger
from .ethereum.eth_erc20 import eth_erc20_top_wallets
from .ethereum.eth_erc721 import eth_erc721_top_wallets
from .ethereum.eth_erc1155 import eth_erc1155_top_wallets


ACTIVE_WALLETS_BP = Blueprint("wallets", url_prefix='/wallets', version=1)

@ACTIVE_WALLETS_BP.get('<chain>/most_active')
# @is_subscribed()
async def most_active(request, chain):
    if chain not in request.app.config.SUPPORTED_CHAINS:
        raise CustomError("chain not suported")

    if not request.args.get("erc_type"):
        raise CustomError("ERC Type is required")

    if not request.args.get("erc_type") in ["ERC20", "ERC721", "ERC1155"]:
        raise CustomError("ERC Type is not valid")

    if not request.args.get("number_of_days"):
        number_of_days = 7
    else: 
        number_of_days = int(request.args.get("number_of_days"))

    if not request.args.get("limit"):
        request.args["limit"] = [1000]
    
    if not request.args.get("skip"):
        request.args["limit"] = [0]
    

    try:
        if request.args.get("erc_type") == "ERC20":
            result = await eth_erc20_top_wallets(number_of_days, request.args.get("limit"))
        elif request.args.get("erc_type") == "ERC721":
            result = await eth_erc721_top_wallets(number_of_days, request.args.get("limit"))
        else:
            result = await eth_erc1155_top_wallets(number_of_days, request.args.get("limit"))
    except Exception as e:
        raise CustomError(e.__str__())

    return Response.success_response(data=result)