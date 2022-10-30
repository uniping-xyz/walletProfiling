
import datetime, json
from typing import Any
from loguru import logger

# await conn.hdel(key, *["expiry", "data"])
# returns False if new data needs to be fetched i.e cache validity expired
async def cache_validity(redis_client: object, key: str, cache_expiry_in_hours: int) -> bool:
    async with redis_client as conn:
        last_cache: str = await conn.hget(key, "expiry")
        now: str = datetime.datetime.now().strftime("%s")
        if not last_cache or int(now)  > int(last_cache):
            logger.warning(f"Cache didnt exists for key=[{key}] or Cache has expired {last_cache} and Now {now}")
            return False
        logger.success(f"Cache hit for key=[{key}]")
        return True

async def get_cache(redis_client: object, key: str) -> str:
    return await redis_client.hget(key, "data")

async def delete_cache(redis_client: object, key: str) -> str:
    return await redis_client.hdel(key)


async def set_cache(redis_client: object, key: str, unserialized_data: any, cache_expiry_in_hours: int):
    await redis_client.hset(key, "data", json.dumps(unserialized_data))
    cache_expiry: str = (datetime.datetime.now() + datetime.timedelta(hours=cache_expiry_in_hours)).strftime("%s")
    await redis_client.hset(key, "expiry", cache_expiry)
    logger.success(f"Cache set for key=[{key}]")
    return 


    