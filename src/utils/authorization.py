from functools import wraps

from sanic.exceptions import SanicException

from sanic import Blueprint
from sanic.response import json
from loguru import logger
from .utils import current_timestamp, checksum_address
import msgpack
from .errors import CustomError





def authorized():
    """Verifies that the token is valid and belongs to an existing user"""
    def decorator(func):
        @wraps(func)
        async def decorated_function(request, *args, **kwargs):
            if request.headers.get("token") is None:
                raise CustomError("No bearer token provided")
            try:
                decoded_token = request.app.config.BRANCA.decode(request.headers["token"])
                # logger.info(f"Decoded token {decoded_token}")
                auth_info = msgpack.loads(decoded_token, raw=False)

            except Exception as e:
                raise CustomError("Invalid token")
            # logger.info(f'CURRENT_TIMESTAMP {current_timestamp()} and TOKEN_VALIDITY {auth_info["validity"]}')
            if current_timestamp() > auth_info["validity"]:
                raise CustomError("Token expired")

            user = await request.app.config.USER.find_one({ 
                        "address": checksum_address(auth_info["address"])},
                        projection={"_id": False, "username": True, "name": True, "address": True, 
                        "notification_count": True, "email": True})
            if not user:   
                raise CustomError("User doesnt exists")

            response = await func(request, user)
            return response
        return decorated_function
    return decorator


def authorized_optional():
    """If token exists and valid it will provide current user info else None"""
    def decorator(func):
        @wraps(func)
        async def decorated_function(request, *args, **kwargs):
            auth_info = {"address": "", "user_details": None}
            if request.headers.get("token") is None:
                pass
            else:
                try:
                    decoded_token = request.app.config.BRANCA.decode(request.headers["token"])
                    auth_info = msgpack.loads(decoded_token, raw=False)
                    user = await request.app.config.USER.find_one({ 
                            "address": checksum_address(auth_info["address"])},
                            projection={"_id": False})
                    if user:
                        auth_info = {"address": auth_info["address"], "user_details": user}
                    else:
                        auth_info = {"address": "", "user_details": None}
                except Exception as e:
                    auth_info = {"address": "", "user_details": None}
                    pass
            response = await func(request, auth_info)
            return response
        return decorated_function
    return 