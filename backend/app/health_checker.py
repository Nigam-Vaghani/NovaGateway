import asyncio
import httpx
import logging
from datetime import datetime, timezone
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.routing import Backend
from app.config import settings
from app.proxy_service import proxy_service

logger = logging.getLogger(__name__)

async def check_backend_health(client: httpx.AsyncClient, backend: Backend) -> bool:
    url = f"{backend.url.rstrip('/')}/health"
    try:
        response = await client.get(url, timeout=5.0)
        return response.status_code == 200
    except Exception as e:
        logger.debug(f"Health check failed for {url}: {e}")
        return False

async def health_check_loop():
    logger.info("Starting health check loop...")
    async with httpx.AsyncClient() as client:
        while True:
            try:
                async with AsyncSessionLocal() as session:
                    stmt = select(Backend)
                    result = await session.execute(stmt)
                    backends = result.scalars().all()

                    for backend in backends:
                        is_healthy = await check_backend_health(client, backend)
                        if backend.is_healthy != is_healthy:
                            logger.info(f"Backend {backend.url} health changed: {backend.is_healthy} -> {is_healthy}")
                            backend.is_healthy = is_healthy
                        
                        if is_healthy:
                            proxy_service.unavailable_backends.discard(backend.id)
                            
                        backend.last_checked = datetime.now(timezone.utc)
                    
                    await session.commit()
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
            
            await asyncio.sleep(settings.HEALTH_CHECK_INTERVAL)
