from functools import wraps

from sanic.exceptions import SanicException

from sanic import Blueprint
from sanic.response import json
from loguru import logger
from .utils import current_timestamp, checksum_address
import msgpack
from .errors import CustomError, SubscriptionRequiredError


def is_subscribed():
    """Verifies that the token is valid and belongs to an existing user"""
    def decorator(func):
        @wraps(func)
        async def decorated_function(request, *args, **kwargs):
            if request.headers.get("token") is None:
                raise CustomError("No bearer token provided")
            try:
                decoded_token = request.app.config.BRANCA.decode(request.headers["token"])
                auth_info = msgpack.loads(decoded_token, raw=False)

            except Exception as e:
                raise CustomError("Invalid token")

            if current_timestamp() > auth_info["validity"]:
                raise CustomError("Token expired")


            if not auth_info.get("subscription"):
                raise SubscriptionRequiredError()

            response = await func(request)
            return response
        return decorated_function
    return decorator

