from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import health, proxy, logs, admin_routing, admin_security, admin_cache
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.security import SecurityHeadersMiddleware, RequestSizeLimitMiddleware, IPFilterMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.logging_config import setup_logging
from app.config import settings
import logging

setup_logging()

logger = logging.getLogger(__name__)

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("NovaGateway starting up...")
    from app.health_checker import health_check_loop
    import asyncio
    health_task = asyncio.create_task(health_check_loop())
    
    yield
    
    logger.info("NovaGateway shutting down...")
    health_task.cancel()
    
    from app.database import engine
    await engine.dispose()
    
    from app.cache_service import cache_service
    await cache_service.redis_client.close()
    
    from app.proxy_service import proxy_service
    await proxy_service.client.aclose()

app = FastAPI(
    title="NovaGateway",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RateLimitMiddleware)
app.add_middleware(IPFilterMiddleware)
app.add_middleware(RequestSizeLimitMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)

app.include_router(health.router)
app.include_router(logs.router)
app.include_router(admin_routing.router)
app.include_router(admin_security.router)
app.include_router(admin_cache.router)
app.include_router(proxy.router)

