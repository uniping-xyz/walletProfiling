
import json
from sanic import Blueprint
from utils.utils import Response
from utils.errors import CustomError
from utils.authorization import is_subscribed
from loguru import logger
from find_addresses.external_calls.s3.erc20.eth_trending_contract_creators import erc20_trending_contract_creators
from find_addresses.external_calls.s3.erc721.eth_trending_contract_creators import erc721_trending_contract_creators
from find_addresses.external_calls.s3.erc1155.eth_trending_contract_creators import erc1155_trending_contract_creators
from find_addresses.external_calls.s3.unknownstandard.eth_trending_contract_creators import unknownstandard_trending_contract_creators

from populate_data.populate_coingecko import check_coingecko_tokens_staleness
from populate_data.populate_blockdaemon import check_blockDaemon_tokens_staleness
from find_addresses.db_calls.erc20.ethereum import search_contract_address as erc20_eth_search
from find_addresses.db_calls.erc721.ethereum import search_contract_address as erc721_eth_search
from find_addresses.db_calls.erc1155.ethereum import search_contract_address as erc1155_eth_search
# from find_addresses.external_calls.s3.erc721.eth_active_wallets import erc721_active_wallets
# from find_addresses.external_calls.s3.erc1155.eth_active_wallets import erc1155_active_wallets


CREATOR_WALLETS_BP = Blueprint("wallet_creators", url_prefix='/wallets/contract_creators', version=1)

"""
Wallets who have deployed the most contracts in an erc type
"""
@CREATOR_WALLETS_BP.get('trending')
# @is_subscribed()
async def trending_contract_creators(request):
    await check_coingecko_tokens_staleness(request.app)
    await check_blockDaemon_tokens_staleness(request.app)
    if request.args.get("chain") not in request.app.config.SUPPORTED_CHAINS:
        raise CustomError("chain not suported")

    if not request.args.get("erc_type"):
        raise CustomError("ERC Type is required")

    if not request.args.get("erc_type") in ["ERC20", "ERC721", "ERC1155", "unknown"]:
        raise CustomError("ERC Type is not valid")

    if not request.args.get("limit"):
        request.args["limit"] = [1000]
    
    try:
        if request.args.get("erc_type") == "ERC20":
            result = await erc20_trending_contract_creators(request.args.get("limit"))

        elif request.args.get("erc_type") == "ERC721":
            result = await erc721_trending_contract_creators(request.args.get("limit"))
        elif request.args.get("erc_type") == "ERC1155":
            result = await erc1155_trending_contract_creators(request.args.get("limit"))
        else:
            result = await unknownstandard_trending_contract_creators(request.args.get("limit"))

    except Exception as e:
        raise CustomError(e.__str__())

    return Response.success_response(data=result, count=len(result), days=120)