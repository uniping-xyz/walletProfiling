
from branca import Branca
from sanic import Blueprint
from utils.utils import Response, future_timestamp
from utils.authorization import is_subscribed
from utils.errors import CustomError
from loguru import logger
import msgpack
ADMIN_BP = Blueprint("admin", url_prefix='/', version=1)


@ADMIN_BP.get('generate_admin_token')
async def test_chain(request):

    # logger.info(request.app.config.SECRET)
    # branca = Branca(key=request.app.config.SECRET)
    payload = {"address": "0x6004d517f31f21e93536794f5CB25F762Fa33B19", 
            "username": "admin", 
            "subscription": True,  
            "validity": future_timestamp(150)}

    authorization = msgpack.dumps(payload)
    token = request.app.config.BRANCA.encode(authorization)
    return Response.success_response(data={"token": token})
    
