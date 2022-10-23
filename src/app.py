from signal import signal, SIGINT
import sys
import json
from sanic import Sanic
from motor.motor_asyncio import AsyncIOMotorClient
from sanic import Blueprint
from loguru import logger
import asyncio
import os
import multiprocessing
from find_addresses.api import FIND_ADDRESSES_BP
from find_addresses.token_search import  TOKEN_SEARCH_BP
from find_addresses.utils import get_ethereum_tags
from find_addresses.top_tokens import MOST_POPULAR_BP
from find_addresses.token_holders import TOKEN_HOLDERS_BP

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
    
 


async def db_connection():
    db_config = app.config[ENVIRONMENT]["DATABASE"]
    uri = f'mongodb://{db_config["user"]}:{ db_config["password"]}@{db_config["ip"]}:{ db_config["port"]}/{db_config["dbname"]}'
    connection = AsyncIOMotorClient(uri)
    db_config = app.config[ENVIRONMENT]["DATABASE"]
    db = connection[db_config["dbname"]]
    app.config.TOKENS = db["tokens"]
    app.config.QUERIES = db["queries"]

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
    
    eth_tags = await get_ethereum_tags(app.config.LUABASE_API_KEY)
    app.config.tags = {}
    app.config.tags.update({"ethereum": [e["label"] for e in eth_tags]})
    
    logger.info(app.config.tags)
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
                            FIND_ADDRESSES_BP,
                            TOKEN_SEARCH_BP,
                            MOST_POPULAR_BP,
                            TOKEN_HOLDERS_BP,
                            url_prefix='/api')
    app.blueprint(APP_BP)
    for route in app.router.routes:
        print(f"/{route.path:60} - {route.name:70} -  {route.methods} [{route.router}]")
    logger.info("Get the swagger doucmentation at /swagger")


    app.run(host="0.0.0.0", port=8001, workers=1, auto_reload=True, access_log=False,  reload_dir="./config")
