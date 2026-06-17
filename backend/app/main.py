from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import health, proxy, logs
from app.middleware.logging import RequestLoggingMiddleware
from app.logging_config import setup_logging
from app.config import settings
import logging

setup_logging()

logger = logging.getLogger(__name__)

app = FastAPI(
    title="NovaGateway",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestLoggingMiddleware)

app.include_router(health.router)
app.include_router(logs.router)
app.include_router(proxy.router)

@app.on_event("startup")
async def startup_event():
    logger.info("NovaGateway starting up...")
