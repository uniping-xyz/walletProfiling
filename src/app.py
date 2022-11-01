from signal import signal, SIGINT
import sys
import json
from sanic import Sanic
from motor.motor_asyncio import AsyncIOMotorClient
from sanic import Blueprint
from loguru import logger
from redis import asyncio as aioredis

import asyncio, datetime
import os
import multiprocessing
from find_addresses.common_address_different_tokens import CMN_ADDR_DIFF_TKNS
from find_addresses.token_search import  TOKEN_SEARCH_BP
from find_addresses.top_tokens import MOST_POPULAR_BP
from find_addresses.token_holders import TOKEN_HOLDERS_BP
from find_addresses.token_transfers import TOKEN_TRANSFERS_BP
from find_addresses.contract_tags import TOKEN_TAGS_BP
from find_addresses.token_stats import TOKEN_STATS_BP
from find_addresses.user_token_balances import USER_TOKEN_BALANCE_BP
from caching.cache_utils import cache_validity, set_cache, get_cache
from sanic_cors import CORS

app = Sanic(__name__)


app.config["API_TITLE"] = "Pingbox"

# Session(app)  # because InMemorySessionInterface used by default
ENVIRONMENT = ""
CORS(app, automatic_options=True)




def close_connections():
    logger.warning('closing database connection')
    app.config.DB_CONN.close()


def load_config():  # pylint: disable=too-many-branches
    with open('./config/config.json', 'r') as f:
        config = json.load(f)
    try:
        app.config.update(config)
        app.config.update({"env": ENVIRONMENT})
        
    except Exception as e:
        print(e)
        raise Exception("Config object couldnt be loaded because of some error")
    
 
async def create_index_tokens(collection):
    index_information = await collection.index_information()
    if not index_information.get("ethereum_index"):
        logger.success("ethereum_index doesnt exists; creating an index on ethereum on tokens collection")
        await collection.create_index(
                'ethereum',
                unique=False,
                sparse=True,
                name='ethereum_index',
                default_language='english')

    index_information = await collection.index_information()
    if not index_information.get("polygon_index"):
        logger.success("polygon_index doesnt exists; creating an index on polygon on tokens collection")
        await collection.create_index(
                'polygon',
                unique=False,
                sparse=True,
                name='polygon_index',
                default_language='english')




async def db_connection():
    db_config = app.config[ENVIRONMENT]["DATABASE"]
    uri = f'mongodb://{db_config["user"]}:{ db_config["password"]}@{db_config["ip"]}:{ db_config["port"]}/{db_config["dbname"]}'
    connection = AsyncIOMotorClient(uri)
    db_config = app.config[ENVIRONMENT]["DATABASE"]
    db = connection[db_config["dbname"]]
    app.config.TOKENS = db["tokens"]
    app.config.QUERIES = db["queries"]
    logger.success(f"Total tokens in DB  {await app.config.TOKENS.count_documents({})}")

    await create_index_tokens( app.config.TOKENS)

    logger.success(f"Mongodb connection established {db}")
    return

@app.after_server_start
async def after_server_start(app, loop):
    load_config()
    await db_connection()
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = app.config[ENVIRONMENT]["GOOGLE_CREDS_JSON_PATH"]
    app.config.bq_polygon_table = app.config[ENVIRONMENT]["BQ_POLYGON_TABLE_NAME"]
    app.config.bq_eth_table = app.config[ENVIRONMENT]["BQ_ETH_TABLE_NAME"]
    app.config.WEB3_PROVIDER = app.config[ENVIRONMENT]["WEB3_PROVIDER"]
    app.config.LUABASE_API_KEY = app.config[ENVIRONMENT]["LUABASE_API_KEY"]
    
    redis = aioredis.from_url(
        "redis://localhost", encoding="utf-8", decode_responses=True
    )

    app.config.REDIS_CLIENT = redis.client()
    for cache_lvls in app.config.CACHING_TTL:
        cache_value = app.config.CACHING_TTL[cache_lvls]
        if cache_value < 3600:
            print(f'{cache_lvls} = {int(app.config.CACHING_TTL[cache_lvls]/60)} Minutes ')
        else:
            print(f'{cache_lvls} = {int(app.config.CACHING_TTL[cache_lvls]/3600)} Hours')

    return

@app.listener('after_server_stop')
async def finish(app, loop):
    logger.info("Stopping the AIOHTTP SESSION")
    loop.run_until_complete(app.aiohttp_session.close())
    await asyncio.sleep(1)
    loop.close()

if __name__ == "__main__":
    workers = multiprocessing.cpu_count()
    ENVIRONMENT = os.environ['APP_ENV']
    if ENVIRONMENT not in ["dev", "mainnet", "testnet"]:
        raise Exception(f'Only possible options are ["dev", "mainnet", "testnet"], given is <<{ENVIRONMENT}>>')
    logger.info(f"The Env is {ENVIRONMENT}")


    APP_BP = Blueprint.group(
                            CMN_ADDR_DIFF_TKNS,
                            TOKEN_SEARCH_BP,
                            MOST_POPULAR_BP,
                            TOKEN_HOLDERS_BP,
                            TOKEN_TRANSFERS_BP,
                            TOKEN_TAGS_BP,
                            TOKEN_STATS_BP,
                            USER_TOKEN_BALANCE_BP,
                            url_prefix='/api')
    app.blueprint(APP_BP)
    for route in app.router.routes:
        print(f"/{route.path:60} - {route.name:70} -  {route.methods} [{route.router}]")
    logger.info("Get the swagger doucmentation at /swagger")


    app.run(host="0.0.0.0", port=8001, workers=1, auto_reload=True, access_log=False,  reload_dir="./config")
