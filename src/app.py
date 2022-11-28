from signal import signal, SIGINT
import json, os
from sanic import Sanic
from motor.motor_asyncio import AsyncIOMotorClient
from sanic import Blueprint
from loguru import logger
from redis import asyncio as aioredis
from branca import Branca
import binascii
from find_addresses.common_address_different_tokens import CMN_ADDR_DIFF_TKNS
from find_addresses.token_search import  TOKEN_SEARCH_BP
from find_addresses.top_tokens import MOST_POPULAR_BP
from find_addresses.token_holders import TOKEN_HOLDERS_BP
from find_addresses.token_transfers import TOKEN_TRANSFERS_BP
from find_addresses.contract_tags import TOKEN_TAGS_BP
from find_addresses.token_stats import TOKEN_STATS_BP
from find_addresses.wallet_stats import USER_TOKEN_BALANCE_BP
from find_addresses.admin import ADMIN_BP
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
 




# async def load_db_secrets(env_path):
#     db_dotenv_path = os.path.join(os.path.dirname(__file__), env_path)
#     config = dotenv_values(db_dotenv_path)
#     user = config.get("MONGO_INITDB_USERNAME")
#     password = config.get("MONGO_INITDB_PASSWORD")
#     ip = config.get("MONGO_IP")
#     port = config.get("MONGO_PORT")
#     db_name = config.get("MONGO_INITDB_DATABASE")
#     uri = f'mongodb://{user}:{password}@{ip}:{port}/{db_name}'
#     logger.info(f"Mongo URI is {uri}")
#     connection = AsyncIOMotorClient(uri)

#     db = connection[db_name]
#     app.config.TOKENS = db["tokens"]
#     app.config.QUERIES = db["queries"]
#     logger.success(f"Total tokens in DB  {await app.config.TOKENS.count_documents({})}")

#     await create_index_tokens( app.config.TOKENS)

#     logger.success(f"Mongodb connection established {db}")
#     return


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
    app.config.POLYGON_ERC20_TOKENS = db["polygon_erc20_tokens"]

    app.config.ETH_ERC721_TOKENS = db["eth_erc721_tokens"]
    app.config.ETH_ERC1155_TOKENS = db["eth_erc1155_tokens"]

    logger.success(f"Total ETH ERC721 tokens in DB  {await app.config.ETH_ERC721_TOKENS.count_documents({})}")
    logger.success(f"Total ETH ERC1155 tokens in DB  {await app.config.ETH_ERC1155_TOKENS.count_documents({})}")
    logger.success(f"Total ETH ERC20 tokens in DB  {await app.config.ETH_ERC20_TOKENS.count_documents({})}")

    
    # logger.success(f"Total tokens in DB  {await app.config.TOKENS.count_documents({})}")


    # await create_index(app.config.TOKENS, "ethereum")
    # await create_index(app.config.TOKENS, "polygon")
    # await create_index(app.config.TOKENS, "tokens")

    await create_index(app.config.ETH_ERC20_TOKENS, "tokens")
    await create_index(app.config.ETH_ERC20_TOKENS, "contracts")
    await create_index(app.config.POLYGON_ERC20_TOKENS, "tokens")
    await create_index(app.config.POLYGON_ERC20_TOKENS, "contracts")
    await create_index(app.config.ETH_ERC721_TOKENS, "tokens")
    await create_index(app.config.ETH_ERC721_TOKENS, "contracts")
    await create_index(app.config.ETH_ERC1155_TOKENS, "tokens")
    await create_index(app.config.ETH_ERC1155_TOKENS, "contracts")


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



@app.after_server_start
async def after_server_start(app, loop):
    ENVIRONMENT = os.environ['APP_ENV']
    await load_db_secrets()

    logger.info(f"Config loded")
    await load_config()
    await secret()
    app.config.bq_polygon_table = os.environ["BQ_POLYGON_TABLE_NAME"]
    app.config.bq_eth_table = os.environ["BQ_ETH_TABLE_NAME"]

    
    redis = aioredis.from_url(
        os.environ["REDIS_URL"], encoding="utf-8", decode_responses=True
    )

    app.config.REDIS_CLIENT = redis.client()
    return



if __name__ == '__main__':

    ENVIRONMENT = os.environ['APP_ENV']

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
    if ENVIRONMENT == "devnet":
        APP_BP = Blueprint.group(APP_BP, ADMIN_BP)

    app.blueprint(APP_BP)
    for route in app.router.routes:
        print(f"/{route.path:60} - {route.name:70} -  {route.methods} [{route.router}]")
    app.run(host="0.0.0.0", port=8080, workers=1, auto_reload=True, access_log=False,  reload_dir="./config")