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
    logger.success(f"Mongodb connection established {db}")
    return


@app.after_server_start
async def after_server_start(app, loop):
    load_config()
    await db_connection()
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
                            url_prefix='/api')
    app.blueprint(APP_BP)
    for route in app.router.routes:
        print(f"/{route.path:60} - {route.name:70} -  {route.methods} [{route.router}]")
    logger.info("Get the swagger doucmentation at /swagger")

    app.run(host="0.0.0.0", port=8080, workers=1, auto_reload=True, access_log=False,  reload_dir="./config")