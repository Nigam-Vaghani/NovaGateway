import httpx
import logging
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from app.config import settings

logger = logging.getLogger(__name__)

HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
}

class ProxyService:
    def __init__(self):
        # Shared connection-pooled client
        self.client = httpx.AsyncClient(limits=httpx.Limits(max_connections=100, max_keepalive_connections=20))

    async def forward_request(self, request: Request, path: str) -> Response:
        # Construct target URL
        base_url = settings.PROXY_TARGET_URL.rstrip('/')
        target_url = f"{base_url}/{path}"
        if request.url.query:
            target_url += f"?{request.url.query}"

        # Prepare headers
        headers = {}
        for key, value in request.headers.items():
            if key.lower() not in HOP_BY_HOP_HEADERS and key.lower() != "host":
                headers[key] = value

        # Add X-Forwarded-For
        client_ip = request.client.host if request.client else "127.0.0.1"
        if "x-forwarded-for" in headers:
            headers["x-forwarded-for"] += f", {client_ip}"
        else:
            headers["x-forwarded-for"] = client_ip

        # Prepare body
        body = await request.body()

        try:
            req = self.client.build_request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
            )
            response = await self.client.send(req)
            
            res_headers = {}
            for key, value in response.headers.items():
                if key.lower() not in HOP_BY_HOP_HEADERS and key.lower() not in ["content-length", "content-encoding"]:
                    res_headers[key] = value
                    
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=res_headers
            )
            
        except httpx.ConnectError as e:
            logger.error(f"Connection error to backend {target_url}: {e}")
            return JSONResponse(status_code=502, content={"error": "Bad Gateway", "message": "Connection refused to backend"})
        except httpx.TimeoutException as e:
            logger.error(f"Timeout connecting to backend {target_url}: {e}")
            return JSONResponse(status_code=504, content={"error": "Gateway Timeout", "message": "Timeout connecting to backend"})
        except Exception as e:
            logger.error(f"Error proxying request to {target_url}: {e}")
            return JSONResponse(status_code=500, content={"error": "Internal Server Error", "message": str(e)})

proxy_service = ProxyService()
