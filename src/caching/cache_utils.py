
import datetime, json
from typing import Any
from loguru import logger

# await conn.hdel(key, *["expiry", "data"])
# returns False if new data needs to be fetched i.e cache validity expired
async def cache_validity(redis_client: object, key: str, cache_expiry_in_secs: int) -> bool:
    async with redis_client as conn:
        
        last_cache_update: str = await conn.hget(key, "updated")
        if not last_cache_update:
            logger.warning(f"CACHE NOT PRESENT: Cache didnt exists for key=[{key}]")
            return False

        now: str = datetime.datetime.now().strftime("%s")

        cache_expiry: str = (datetime.datetime.fromtimestamp(int(last_cache_update)) + datetime.timedelta(seconds=cache_expiry_in_secs)).strftime("%s")

        if int(now)  > int(cache_expiry):
            logger.warning(f"CACHE MISS: Cache for key=[{key}] expired {int(now) - int(cache_expiry)} seconds ago ")
            return False

        logger.success(f"CACHE HIT: Cache for key=[{key}] will expire in {int(cache_expiry) - int(now)} seconds")        
        return True

async def get_cache(redis_client: object, key: str) -> str:
    return await redis_client.hget(key, "data")

async def delete_cache(redis_client: object, key: str) -> str:
    return await redis_client.hdel(key)


async def set_cache(redis_client: object, key: str, unserialized_data: any):
    await redis_client.hset(key, "data", json.dumps(unserialized_data))
    updated: str = datetime.datetime.now().strftime("%s")
    await redis_client.hset(key, "updated", updated)
    logger.success(f"Cache set for key=[{key}]")
    return 


    