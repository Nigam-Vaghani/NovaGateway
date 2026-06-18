import time
import asyncio
import logging
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.database import AsyncSessionLocal
from app.models.request_log import RequestLog

logger = logging.getLogger(__name__)

async def save_request_log(log_data: dict):
    async with AsyncSessionLocal() as session:
        log_entry = RequestLog(**log_data)
        session.add(log_entry)
        await session.commit()

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        
        # Initialize state properties to default values
        request.state.target_backend = None
        request.state.proxy_error = None
        request.state.cache_hit = False
        
        response = None
        try:
            response = await call_next(request)
        except Exception as e:
            request.state.proxy_error = str(e)
            raise e
        finally:
            process_time_ms = (time.time() - start_time) * 1000
            
            client_ip = request.client.host if request.client else None
            # X-Forwarded-For might be present
            forwarded_for = request.headers.get("X-Forwarded-For")
            if forwarded_for:
                client_ip = forwarded_for.split(",")[0].strip()

            status_code = response.status_code if response else 500

            log_data = {
                "client_ip": client_ip,
                "method": request.method,
                "path": request.url.path,
                "target_backend": getattr(request.state, "target_backend", None),
                "status_code": status_code,
                "latency_ms": process_time_ms,
                "response_size": int(response.headers.get("content-length", 0)) if response else 0,
                "error": getattr(request.state, "proxy_error", None),
                "cache_hit": getattr(request.state, "cache_hit", False),
            }
            
            logger.info("Request processed", extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": status_code,
                "latency_ms": round(process_time_ms, 2)
            })
            
            # Save log asynchronously
            asyncio.create_task(save_request_log(log_data))
            
        if response:
            response.headers["X-Request-ID"] = request_id
            
        return response
