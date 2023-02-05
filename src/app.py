from signal import signal, SIGINT
import json, os
from sanic import Sanic
from motor.motor_asyncio import AsyncIOMotorClient
from sanic import Blueprint
from loguru import logger
# from redis import asyncio as aioredis
# import aioredis
import redis.asyncio as redis
from branca import Branca
import boto3
import binascii
from find_addresses.common_address_different_tokens import CMN_ADDR_DIFF_TKNS
from token_search.api import  TOKEN_SEARCH_BP
from top_tokens.api import MOST_POPULAR_BP
from token_holders.api import TOKEN_HOLDERS_BP
from token_stats.api import TOKEN_STATS_BP
from wallet_stats.api import USER_TOKEN_BALANCE_BP
from find_addresses.admin import ADMIN_BP
from most_active_wallets.api import ACTIVE_WALLETS_BP
# from find_addresses.contract_creators import CREATOR_WALLETS_BP
from categories.categories import CATEGORIES_BP


from utils.errors import ERRORS_BP
from dotenv import load_dotenv, dotenv_values

from sanic_cors import CORS

app = Sanic("uniping")
CORS(app, automatic_options=True)


async def secret():
    app.config.BRANCA = Branca(key=binascii.unhexlify(os.environ["SECRET"]))

    return

def close_connections():
    logger.warning('closing database connection')
    app.config.DB_CONN.close()


async def load_config():  # pylint: disable=too-many-branches

    with open('./config/config.json', 'r') as f:
        config = json.load(f)
    try:
        app.config.update(config)        
    except Exception as e:
        print(e)
        raise Exception("Config object couldnt be loaded because of some error")
    return 

async def load_db_secrets():

    user = os.environ["MONGO_INITDB_USERNAME"]
    password = os.environ["MONGO_INITDB_PASSWORD"]
    ip = os.environ["MONGO_IP"]
    port = os.environ["MONGO_PORT"]
    db_name = os.environ["MONGO_INITDB_DATABASE"]
    uri = f'mongodb://{user}:{password}@{ip}:{port}/{db_name}'
    logger.info(f"Mongo URI is {uri}")
    connection = AsyncIOMotorClient(uri)

    db = connection[db_name]
    # app.config.TOKENS = db["tokens"]
    app.config.QUERIES = db["queries"]
    app.config.ETH_ERC20_TOKENS = db["eth_erc20_tokens"]
    app.config.COINGECKO_ETH_ERC20_TOKENS = db["coingecko_eth_erc20_tokens"]
    app.config.POLYGON_ERC20_TOKENS = db["polygon_erc20_tokens"]

    app.config.ETH_ERC721_TOKENS = db["eth_erc721_tokens"]
    app.config.ETH_ERC1155_TOKENS = db["eth_erc1155_tokens"]

    logger.success(f"Total ETH ERC721 tokens in DB  {await app.config.ETH_ERC721_TOKENS.count_documents({})}")
    logger.success(f"Total ETH ERC1155 tokens in DB  {await app.config.ETH_ERC1155_TOKENS.count_documents({})}")
    logger.success(f"Total ETH ERC20 tokens in DB  {await app.config.ETH_ERC20_TOKENS.count_documents({})}")


    await create_index(app.config.ETH_ERC20_TOKENS, "tokens")
    await create_index(app.config.ETH_ERC20_TOKENS, "contracts")
    await create_index(app.config.POLYGON_ERC20_TOKENS, "tokens")
    await create_index(app.config.POLYGON_ERC20_TOKENS, "contracts")
    await create_index(app.config.ETH_ERC721_TOKENS, "tokens")
    await create_index(app.config.ETH_ERC721_TOKENS, "contracts")
    await create_index(app.config.ETH_ERC1155_TOKENS, "tokens")
    await create_index(app.config.ETH_ERC1155_TOKENS, "contracts")
    await create_unique_index(app.config.COINGECKO_ETH_ERC20_TOKENS, "name")


    logger.success(f"Mongodb connection established {db}")
    return

async def create_index(collection, field):
    index_information = await collection.index_information()
    if not index_information.get(f"{field}_index"):
        logger.success(f"{field}_index doesnt exists; creating an index on collection")
        await collection.create_index(
                field,
                unique=False,
                sparse=True,
                name=f"{field}_index",
                default_language='english')


async def create_unique_index(collection, field):
    index_information = await collection.index_information()
    if not index_information.get(f"{field}_index"):
        logger.success(f"{field}_index doesnt exists; creating an index on collection")
        await collection.create_index(
                field,
                unique=True,
                sparse=True,
                name=f"{field}_index",
                default_language='english')

@app.after_server_start
async def after_server_start(app, loop):
    ENVIRONMENT = os.environ['APP_ENV']
    await load_db_secrets()
    logger.info(f"Config loded")
    await load_config()
    await secret()
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = f'./config/{ENVIRONMENT}/gcloud_secrets.json'

    app.config.bq_polygon_table = os.environ["BQ_POLYGON_TABLE_NAME"]
    app.config.bq_eth_table = os.environ["BQ_ETH_TABLE_NAME"]

    # redis = aioredis.from_url(
    #     os.environ["REDIS_URL"], encoding="utf-8", decode_responses=True
    # )
    # app.config.REDIS_CLIENT = redis.client()

    # pool = aioredis.ConnectionPool.from_url(
    #     os.environ["REDIS_URL"], decode_responses=True
    # )
    # app.config.REDIS_CLIENT = aioredis.Redis(connection_pool=pool)

#     pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
# >>> r = redis.Redis(connection_pool=pool)
    app.config.REDIS_CLIENT = redis.Redis.from_url(os.environ["REDIS_URL"])
    print(f"Redis ping successful: {await app.config.REDIS_CLIENT.ping()}")
    return

if __name__ == '__main__':

    ENVIRONMENT = os.environ['APP_ENV']

    logger.info(f"The Env is {ENVIRONMENT}")
    APP_BP = Blueprint.group(CATEGORIES_BP,
                            CMN_ADDR_DIFF_TKNS,
                            TOKEN_SEARCH_BP,
                            MOST_POPULAR_BP,
                            TOKEN_HOLDERS_BP,
                            TOKEN_STATS_BP,
                            USER_TOKEN_BALANCE_BP,
                            ERRORS_BP,
                            ACTIVE_WALLETS_BP,
                            url_prefix='/api')
    if ENVIRONMENT == "devnet":
        APP_BP = Blueprint.group(APP_BP, ADMIN_BP)
    app.blueprint(APP_BP)
    for route in app.router.routes:
        print(f"/{route.path:30} - {route.name:40} -  {route.methods}")
    app.run(host="0.0.0.0", port=8080, workers=1, auto_reload=True, access_log=False,  reload_dir="./config")