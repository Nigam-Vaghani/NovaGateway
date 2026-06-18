from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import settings
from app.database import AsyncSessionLocal
from app.models.security import IPRule
from sqlalchemy import select
import ipaddress

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                if size > settings.MAX_REQUEST_SIZE_MB * 1024 * 1024:
                    return JSONResponse(
                        status_code=413,
                        content={"error": "Payload Too Large"}
                    )
            except ValueError:
                pass
        return await call_next(request)

class IPFilterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip_str = request.client.host if request.client else "127.0.0.1"
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip_str = forwarded_for.split(",")[0].strip()

        try:
            client_ip = ipaddress.ip_address(client_ip_str)
        except ValueError:
            return JSONResponse(status_code=400, content={"error": "Invalid IP address"})

        async with AsyncSessionLocal() as session:
            result = await session.execute(select(IPRule))
            rules = result.scalars().all()

            allow_rules = []
            block_rules = []

            for rule in rules:
                try:
                    network = ipaddress.ip_network(rule.ip_cidr, strict=False)
                    if rule.rule_type == 'block':
                        block_rules.append(network)
                    elif rule.rule_type == 'allow':
                        allow_rules.append(network)
                except ValueError:
                    continue

            # Check block list first
            for network in block_rules:
                if client_ip in network:
                    return JSONResponse(status_code=403, content={"error": "Forbidden: IP blocked"})

            # Check allow list if it's non-empty
            if allow_rules:
                allowed = False
                for network in allow_rules:
                    if client_ip in network:
                        allowed = True
                        break
                if not allowed:
                    return JSONResponse(status_code=403, content={"error": "Forbidden: IP not allowed"})

        return await call_next(request)
