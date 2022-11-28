
import json
import aiohttp
from sanic import Blueprint
from utils.utils import Response
from utils.errors import CustomError
from utils.authorization import is_subscribed
from loguru import logger
from find_addresses.external_calls import luabase_token_transfers

TOKEN_TRANSFERS_BP = Blueprint("transfers", url_prefix='/transfers', version=1)



@TOKEN_TRANSFERS_BP.get('token_transfers')
@is_subscribed()
async def token_transfers(request):
    if request.args.get("chain") not in request.app.config.SUPPORTED_CHAINS:
        raise CustomError("chain not suported")

    if not request.args.get("erc_type"):
        raise CustomError("erc_type is required")

    if not request.args.get("erc_type") in ['ERC721', 'ERC20', 'ERC1155']:
        raise CustomError("Not a valid erc_type")

    if not request.args.get("contract_address"):
        raise CustomError("contract_address is required")



    if not request.args.get("limit"):
        limit = 25
    else:
        limit = request.args.get("limit")

    if not request.args.get("offset"):
        offset = 0
    else:
        offset = request.args.get("offset")


    async with aiohttp.ClientSession() as session:
        if request.args.get("erc_type") in ['ERC721', 'ERC1155']:

            response = await luabase_token_transfers.search_contract_nft_transfers( 
                    request.args.get("contract_address"), limit, offset)
        else:
            response = await luabase_token_transfers.search_contract_erc20_transfers(
                    request.args.get("contract_address"), limit, offset)

    return Response.success_response(data=response)