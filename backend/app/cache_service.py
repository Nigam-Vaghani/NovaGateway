import hashlib
import logging
import redis.asyncio as redis
from app.config import settings

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        # decode_responses=False to handle raw bytes
        self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=False)

    def generate_key(self, method: str, path: str, query_string: str) -> str:
        raw_key = f"{method}:{path}:{query_string}"
        key_hash = hashlib.md5(raw_key.encode('utf-8')).hexdigest()
        return f"cache:{key_hash}"

    async def get_cached(self, key: str) -> bytes | None:
        try:
            return await self.redis_client.get(key)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    async def set_cached(self, key: str, value: bytes, ttl: int):
        if ttl <= 0:
            return
        try:
            await self.redis_client.setex(key, ttl, value)
        except Exception as e:
            logger.error(f"Cache set error: {e}")

    async def invalidate(self, pattern: str):
        try:
            # We need a decode_responses=True client just for matching pattern properly, 
            # or we ensure the pattern is bytes. The pattern string gets converted automatically.
            cursor = 0
            while True:
                cursor, keys = await self.redis_client.scan(cursor, match=pattern, count=100)
                if keys:
                    await self.redis_client.delete(*keys)
                if cursor == 0:
                    break
        except Exception as e:
            logger.error(f"Cache invalidate error: {e}")

    async def get_stats(self) -> dict:
        try:
            info = await self.redis_client.info('memory')
            keyspace = await self.redis_client.info('keyspace')
            
            # info keyspace format is usually like {'db0': {'keys': 5, 'expires': 0, 'avg_ttl': 0}}
            db_key = list(keyspace.keys())[0] if keyspace else None
            total_keys = keyspace[db_key]['keys'] if db_key and 'keys' in keyspace[db_key] else 0

            return {
                "total_keys": total_keys,
                "used_memory_human": info.get("used_memory_human", "0B"),
                "used_memory": info.get("used_memory", 0)
            }
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {}

cache_service = CacheService()
