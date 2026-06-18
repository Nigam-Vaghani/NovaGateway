import time
import json
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import settings
import redis.asyncio as redis
import logging

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

    async def dispatch(self, request: Request, call_next):
        # Health checks bypass rate limiting
        if request.url.path == "/health":
            return await call_next(request)

        client_ip_str = request.client.host if request.client else "127.0.0.1"
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip_str = forwarded_for.split(",")[0].strip()

        key = f"rate_limit:{client_ip_str}"
        now = time.time()
        window_start = now - settings.RATE_LIMIT_WINDOW

        try:
            # Redis sliding window
            async with self.redis_client.pipeline(transaction=True) as pipe:
                # Remove timestamps older than window
                pipe.zremrangebyscore(key, 0, window_start)
                # Count requests in window
                pipe.zcard(key)
                # Add current request
                pipe.zadd(key, {str(now): now})
                # Set expiry on key to clean up automatically
                pipe.expire(key, settings.RATE_LIMIT_WINDOW)
                
                results = await pipe.execute()
                
            request_count = results[1]

            if request_count >= settings.RATE_LIMIT_REQUESTS:
                # Need to find the oldest request to calculate Retry-After
                oldest = await self.redis_client.zrange(key, 0, 0, withscores=True)
                retry_after = settings.RATE_LIMIT_WINDOW
                if oldest:
                    oldest_time = oldest[0][1]
                    retry_after = int(settings.RATE_LIMIT_WINDOW - (now - oldest_time))
                    if retry_after < 0:
                        retry_after = settings.RATE_LIMIT_WINDOW

                return JSONResponse(
                    status_code=429,
                    content={"error": "Too Many Requests"},
                    headers={"Retry-After": str(retry_after)}
                )

        except Exception as e:
            logger.error(f"Redis rate limiting error: {e}")
            # Fail open if Redis is down
            pass

        return await call_next(request)
