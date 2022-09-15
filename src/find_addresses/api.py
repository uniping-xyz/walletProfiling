from sanic import Blueprint
import datetime
from loguru import logger
import requests
from utils.utils import Response
from utils.authorization import authorized, authorized_optional

FIND_ADDRESSES_BP = Blueprint("channels", url_prefix='/find_address', version=1)


@FIND_ADDRESSES_BP.get('notification_fee')
async def posts_created(request):
    amafans_channel_object = request.app.config.amafans_channel_object
    return Response.success_response(data=[])