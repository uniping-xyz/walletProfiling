


from decimal import Decimal
from sanic import json, response
import datetime
from sanic import request
from .errors import CustomError
from loguru import logger
import asyncio
from functools import wraps, partial
from json import dumps
from bson.decimal128 import Decimal128
import json

def current_timestamp():
    current_time = datetime.datetime.now(datetime.timezone.utc)
    unix_timestamp = current_time.timestamp() # works if Python >= 3.3
    return unix_timestamp


def future_timestamp(minutes: int):
    timestamp = current_timestamp()
    future_timestamp = timestamp + (minutes * 60)  # 5 min * 60 second
    return future_timestamp


def wrap(func):
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)
    return run


def skip_limit(request):
    skip = int(request.args.get("skip")) if request.args.get("skip") else 0
    limit = int(request.args.get("limit")) if request.args.get("limit") else 10
    return (skip, limit)

def check_args(args: list, request: request.Request) -> dict:
    arguments = {}
    if not request.json:
        raise CustomError(f"post arguments are missing in the request", status_code=500)
    for arg in args:
        if request.json.get(arg) is None:
            # raise errors.ApiInternalError({"message": f"{arg} is missing in the post data"})
            raise CustomError(f"{arg} is missing in the post data", status_code=501)
        arguments.update({arg: request.json[arg]})
    return arguments

def check_signature(msg, signature):
    try:
        message = encode_defunct(text=msg)
        signer = w3.eth.account.recover_message(message, signature=signature)
    except Exception as e:
        logger.error(e.__str__())
        raise CustomError("Invalid Signatures")


    return signer


def current_timestamp():
    current_time = datetime.datetime.now(datetime.timezone.utc)
    unix_timestamp = current_time.timestamp() # works if Python >= 3.3
    return unix_timestamp


def future_timestamp(minutes: int):
    timestamp = current_timestamp()
    future_timestamp = timestamp + (minutes * 60)  # 5 min * 60 second
    return future_timestamp

def checksum_address(address):
    try:
        # logger.info(f"Checking checksum of the address {address}")
        _address = web3.Web3.toChecksumAddress(address.lower())
    except web3.exceptions.InvalidAddress:
        message = f"Invalid checksum for address {address} in conversational_data"
        logger.error(message)
        raise CustomError(message)
    return _address


def is_valid_eth_address(address):
    valid = False
    try:
        valid = web3.Web3.isAddress(address)
    except Exception as e:
       pass
    return valid


def json_handler():
    def json_serialize_helper(data):
        """JSON serializer for objects not serializable by default json code"""
        
        if isinstance(data, datetime.datetime):
            return data.strftime('%s')
        if isinstance(data, Decimal128):
            return str(data)
        logger.error("Type %s not serializable" % type(data))
        raise TypeError ("Type %s not serializable" % type(data))
    return json_serialize_helper


        
class Response:
    @staticmethod
    def success_response(message=None, caching_ttl=0, days=90, count=0, data={}):
        
        return response.json(
            {
            "message": message,
            "count": count,
            "data": data,
            "caching_ttl": caching_ttl,
            "days": days,
            "error": False, 
            "success": True
            }, 
            200,
            None,
            "application/json",
            dumps,
            default=json_handler()
            )

    @staticmethod
    def success_response_type(data={}):
        return {
            "message": str,
            "count": int,
            "data": data, 
            "error": bool, 
            "success": bool
            }
    
    @staticmethod
    def error_response(message=None):
        return response.json(
            {
            "message": message,
            "data": {}, 
            "error": True, 
            "success": False
            })

    @staticmethod
    def error_response_type(message=None):
        return {
            "message": str,
            "data": {}, 
            "error": bool, 
            "success": bool
            }


