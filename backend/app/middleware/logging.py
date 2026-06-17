import time
import asyncio
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.database import AsyncSessionLocal
from app.models.request_log import RequestLog

async def save_request_log(log_data: dict):
    async with AsyncSessionLocal() as session:
        log_entry = RequestLog(**log_data)
        session.add(log_entry)
        await session.commit()

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
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

            log_data = {
                "client_ip": client_ip,
                "method": request.method,
                "path": request.url.path,
                "target_backend": getattr(request.state, "target_backend", None),
                "status_code": response.status_code if response else 500,
                "latency_ms": process_time_ms,
                "response_size": int(response.headers.get("content-length", 0)) if response else 0,
                "error": getattr(request.state, "proxy_error", None),
                "cache_hit": getattr(request.state, "cache_hit", False),
            }
            
            # Save log asynchronously
            asyncio.create_task(save_request_log(log_data))
            
        return response
