


import json
import asyncio
from sanic import Blueprint
from utils.utils import Response
from utils.errors import CustomError
from loguru import logger
from caching.cache_utils import cache_validity, get_cache, set_cache, delete_cache
from .ethereum.eth_millionaires_w_nfts import eth_millionaires_w_nfts
from .ethereum.token_millionaires_w_nfts import token_millionaires_w_nfts
from .ethereum.wallet_millionaires_w_nfts import wallet_millionaires_w_nfts

from .ethereum.wallet_millionaires_cex import wallet_millionaires_cex
from .ethereum.eth_millionaires_cex import eth_millionaires_cex
from .ethereum.token_millionaires_cex import token_millionaires_cex

from .ethereum.eth_millionaires_dex import eth_millionaires_dex
from .ethereum.token_millionaires_dex import token_millionaires_dex
from .ethereum.wallet_milllionaries_dex import wallet_millionaires_dex

from .polygon.most_active_nft_wallets_7day import polygon_erc721_7day

WALLET_TAGS_BP = Blueprint("wallettags", url_prefix='/wallettags', version=1)


def make_query_string(request_args: dict, args_list: list) -> str:
    query_string = ""
    for (key, value) in request_args.items():
        if key in args_list:
            if type(value) == list:
                value = value[0]
            query_string += f"&{key}={value}"
    return query_string[1:]

#---------------------------- Centralised exchanges ------------------------------------------

async def wallet_millionaires_cex_caching(app: object, caching_key: str, caching_ttl:int, request_args: dict) -> any: 
    cache_valid = await cache_validity(app.config.REDIS_CLIENT, caching_key, caching_ttl)
    if not cache_valid:
        data = await wallet_millionaires_cex()
        if data:
            await set_cache(app.config.REDIS_CLIENT, caching_key, data)
        return data
    result= await get_cache(app.config.REDIS_CLIENT, caching_key)
    return json.loads(result)

@WALLET_TAGS_BP.get('<chain>/wallet_millionaires_cex')
async def wallet_millionaires_cex_handler(request, chain):
    caching_ttl =  request.app.config.CACHING_TTL['LEVEL_EIGHT']
    if chain not in request.app.config["SUPPORTED_CHAINS"]:
        raise CustomError("chain is required")
    request.args["chain"] = chain
    caching_key = f"{request.route.path.replace('<chain:str>', chain)}"
    data = await wallet_millionaires_cex_caching(request.app, caching_key, caching_ttl, request.args)
    return Response.success_response(data=data, caching_ttl=caching_ttl, days=-1)


async def token_millionaires_cex_caching(app: object, caching_key: str, caching_ttl:int, request_args: dict) -> any: 
    cache_valid = await cache_validity(app.config.REDIS_CLIENT, caching_key, caching_ttl)
    if not cache_valid:
        data = await token_millionaires_cex()
        if data:
            await set_cache(app.config.REDIS_CLIENT, caching_key, data)
        return data
    result= await get_cache(app.config.REDIS_CLIENT, caching_key)
    return json.loads(result)

@WALLET_TAGS_BP.get('<chain>/token_millionaires_cex')
async def token_millionaires_cex_handler(request, chain):
    caching_ttl =  request.app.config.CACHING_TTL['LEVEL_EIGHT']
    if chain not in request.app.config["SUPPORTED_CHAINS"]:
        raise CustomError("chain is required")
    request.args["chain"] = chain
    caching_key = f"{request.route.path.replace('<chain:str>', chain)}"
    data = await token_millionaires_cex_caching(request.app, caching_key, caching_ttl, request.args)
    return Response.success_response(data=data, caching_ttl=caching_ttl, days=-1)


async def eth_millionaires_cex_caching(app: object, caching_key: str, caching_ttl:int, request_args: dict) -> any: 
    cache_valid = await cache_validity(app.config.REDIS_CLIENT, caching_key, caching_ttl)
    if not cache_valid:
        data = await eth_millionaires_cex()
        if data:
            await set_cache(app.config.REDIS_CLIENT, caching_key, data)
        return data
    result= await get_cache(app.config.REDIS_CLIENT, caching_key)
    return json.loads(result)

@WALLET_TAGS_BP.get('<chain>/eth_millionaires_cex')
async def eth_millionaires_cex_handler(request, chain):
    caching_ttl =  request.app.config.CACHING_TTL['LEVEL_EIGHT']
    if chain not in request.app.config["SUPPORTED_CHAINS"]:
        raise CustomError("chain is required")
    request.args["chain"] = chain
    caching_key = f"{request.route.path.replace('<chain:str>', chain)}"
    data = await eth_millionaires_cex_caching(request.app, caching_key, caching_ttl, request.args)
    return Response.success_response(data=data, caching_ttl=caching_ttl, days=-1)



#---------------------------- DECentralised exchanges ------------------------------------------

async def wallet_millionaires_dex_caching(app: object, caching_key: str, caching_ttl:int, request_args: dict) -> any: 
    cache_valid = await cache_validity(app.config.REDIS_CLIENT, caching_key, caching_ttl)
    if not cache_valid:
        data = await wallet_millionaires_dex()
        if data:
            await set_cache(app.config.REDIS_CLIENT, caching_key, data)
        return data
    result= await get_cache(app.config.REDIS_CLIENT, caching_key)
    return json.loads(result)

@WALLET_TAGS_BP.get('<chain>/wallet_millionaires_dex')
async def wallet_millionaires_dex_handler(request, chain):
    caching_ttl =  request.app.config.CACHING_TTL['LEVEL_EIGHT']
    if chain not in request.app.config["SUPPORTED_CHAINS"]:
        raise CustomError("chain is required")
    request.args["chain"] = chain
    caching_key = f"{request.route.path.replace('<chain:str>', chain)}"
    data = await wallet_millionaires_dex_caching(request.app, caching_key, caching_ttl, request.args)
    return Response.success_response(data=data, caching_ttl=caching_ttl, days=-1)


async def token_millionaires_dex_caching(app: object, caching_key: str, caching_ttl:int, request_args: dict) -> any: 
    cache_valid = await cache_validity(app.config.REDIS_CLIENT, caching_key, caching_ttl)
    if not cache_valid:
        data = await token_millionaires_dex()
        if data:
            await set_cache(app.config.REDIS_CLIENT, caching_key, data)
        return data
    result= await get_cache(app.config.REDIS_CLIENT, caching_key)
    return json.loads(result)

@WALLET_TAGS_BP.get('<chain>/token_millionaires_dex')
async def token_millionaires_dex_handler(request, chain):
    caching_ttl =  request.app.config.CACHING_TTL['LEVEL_EIGHT']
    if chain not in request.app.config["SUPPORTED_CHAINS"]:
        raise CustomError("chain is required")
    request.args["chain"] = chain
    caching_key = f"{request.route.path.replace('<chain:str>', chain)}"
    data = await token_millionaires_dex_caching(request.app, caching_key, caching_ttl, request.args)
    return Response.success_response(data=data, caching_ttl=caching_ttl, days=-1)


async def eth_millionaires_dex_caching(app: object, caching_key: str, caching_ttl:int, request_args: dict) -> any: 
    cache_valid = await cache_validity(app.config.REDIS_CLIENT, caching_key, caching_ttl)
    if not cache_valid:
        data = await eth_millionaires_dex()
        if data:
            await set_cache(app.config.REDIS_CLIENT, caching_key, data)
        return data
    result= await get_cache(app.config.REDIS_CLIENT, caching_key)
    return json.loads(result)

@WALLET_TAGS_BP.get('<chain>/eth_millionaires_dex')
async def eth_millionaires_dex_handler(request, chain):
    caching_ttl =  request.app.config.CACHING_TTL['LEVEL_EIGHT']
    if chain not in request.app.config["SUPPORTED_CHAINS"]:
        raise CustomError("chain is required")
    request.args["chain"] = chain
    caching_key = f"{request.route.path.replace('<chain:str>', chain)}"
    data = await eth_millionaires_dex_caching(request.app, caching_key, caching_ttl, request.args)
    return Response.success_response(data=data, caching_ttl=caching_ttl, days=-1)

#-----------------------------------------------------------------------------------------












async def wallet_millionaires_caching(app: object, caching_key: str, caching_ttl:int, request_args: dict) -> any: 
    cache_valid = await cache_validity(app.config.REDIS_CLIENT, caching_key, caching_ttl)
    if not cache_valid:
        data = await wallet_millionaires_w_nfts()
        if data:
            await set_cache(app.config.REDIS_CLIENT, caching_key, data)
        return data
    result= await get_cache(app.config.REDIS_CLIENT, caching_key)
    return json.loads(result)

@WALLET_TAGS_BP.get('<chain>/wallet_millionaires')
async def wallet_millionaires(request, chain):
    caching_ttl =  request.app.config.CACHING_TTL['LEVEL_EIGHT']
    if chain not in request.app.config["SUPPORTED_CHAINS"]:
        raise CustomError("chain is required")
    request.args["chain"] = chain
    caching_key = f"{request.route.path.replace('<chain:str>', chain)}"
    data = await wallet_millionaires_caching(request.app, caching_key, caching_ttl, request.args)
    return Response.success_response(data=data, caching_ttl=caching_ttl, days=-1)


async def native_token_millionaires_caching(app: object, caching_key: str, caching_ttl:int, request_args: dict) -> any: 
    cache_valid = await cache_validity(app.config.REDIS_CLIENT, caching_key, caching_ttl)

    if not cache_valid:
        data = await eth_millionaires_w_nfts()
        if data:
            await set_cache(app.config.REDIS_CLIENT, caching_key, data)
        return data
    result= await get_cache(app.config.REDIS_CLIENT, caching_key)
    return json.loads(result)

@WALLET_TAGS_BP.get('<chain>/native_token_millionaires')
async def native_token_millionaires(request, chain):

    caching_ttl =  request.app.config.CACHING_TTL['LEVEL_EIGHT']

    if chain not in request.app.config["SUPPORTED_CHAINS"]:
        raise CustomError("chain is required")
    request.args["chain"] = chain

    caching_key = f"{request.route.path.replace('<chain:str>', chain)}"

    data = await native_token_millionaires_caching(request.app, caching_key, caching_ttl, request.args)
         
    return Response.success_response(data=data, caching_ttl=caching_ttl, days=-1)

async def token_millionaires_caching(app: object, caching_key: str, caching_ttl:int, request_args: dict) -> any: 
    cache_valid = await cache_validity(app.config.REDIS_CLIENT, caching_key, caching_ttl)

    if not cache_valid:
        data = await token_millionaires_w_nfts()
        if data:
            await set_cache(app.config.REDIS_CLIENT, caching_key, data)
        return data
    result= await get_cache(app.config.REDIS_CLIENT, caching_key)
    return json.loads(result)

@WALLET_TAGS_BP.get('<chain>/token_millionaires')
async def token_millionaires(request, chain):

    caching_ttl =  request.app.config.CACHING_TTL['LEVEL_EIGHT']

    if chain not in request.app.config["SUPPORTED_CHAINS"]:
        raise CustomError("chain is required")
    request.args["chain"] = chain

    caching_key = f"{request.route.path.replace('<chain:str>', chain)}"

    data = await token_millionaires_caching(request.app, caching_key, caching_ttl, request.args)
         
    return Response.success_response(data=data, caching_ttl=caching_ttl, days=-1)

async def polygon_nfts_caching(app: object, caching_key: str, caching_ttl:int, request_args: dict) -> any: 
    cache_valid = await cache_validity(app.config.REDIS_CLIENT, caching_key, caching_ttl)

    if not cache_valid:
        data = await polygon_erc721_7day()
        if data:
            await set_cache(app.config.REDIS_CLIENT, caching_key, data)
        return data
    result= await get_cache(app.config.REDIS_CLIENT, caching_key)
    return json.loads(result)

@WALLET_TAGS_BP.get('<chain>/polygon_nfts')
async def polygon_nfts(request, chain):

    caching_ttl =  request.app.config.CACHING_TTL['LEVEL_EIGHT']

    if chain not in request.app.config["SUPPORTED_CHAINS"]:
        raise CustomError("chain is required")
    request.args["chain"] = chain

    caching_key = f"{request.route.path.replace('<chain:str>', chain)}"

    data = await polygon_nfts_caching(request.app, caching_key, caching_ttl, request.args)
         
    return Response.success_response(data=data, caching_ttl=caching_ttl, days=-1)