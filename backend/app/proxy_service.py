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
        self.unavailable_backends = set()

    async def forward_request(self, request: Request, path: str) -> Response:
        from app.routing_service import routing_service
        from app.load_balancer import get_load_balancer

        route, backends = await routing_service.resolve_route(path)
        
        if not route:
            return JSONResponse(status_code=404, content={"error": "Not Found", "message": "No matching route found"})
            
        if not route.is_active:
            return JSONResponse(status_code=503, content={"error": "Service Unavailable", "message": "Route is disabled"})
            
        lb = get_load_balancer(settings.LOAD_BALANCER_STRATEGY)
        
        last_error = None
        status_code_for_error = 502

        # Read body once since we might retry
        body = await request.body()

        for attempt in range(settings.MAX_RETRIES):
            available_backends = [b for b in backends if b.id not in self.unavailable_backends]
            
            if not available_backends:
                if attempt == 0:
                    return JSONResponse(status_code=503, content={"error": "Service Unavailable", "message": "No healthy backends available"})
                else:
                    break

            backend = lb.select_backend(available_backends)
            
            # Construct target URL
            base_url = backend.url.rstrip('/')
            
            forward_path = path
            if route.strip_prefix:
                prefix = route.path_prefix.strip('/')
                if prefix and forward_path.startswith(prefix):
                    forward_path = forward_path[len(prefix):].lstrip('/')
                    
            target_url = f"{base_url}/{forward_path}"
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

            request.state.target_backend = target_url

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
                request.state.proxy_error = f"Connection error: {e}"
                last_error = f"Connection refused to backend: {e}"
                status_code_for_error = 502
                self.unavailable_backends.add(backend.id)
            except httpx.TimeoutException as e:
                logger.error(f"Timeout connecting to backend {target_url}: {e}")
                request.state.proxy_error = f"Timeout error: {e}"
                last_error = f"Timeout connecting to backend: {e}"
                status_code_for_error = 504
                self.unavailable_backends.add(backend.id)
            except Exception as e:
                logger.error(f"Error proxying request to {target_url}: {e}")
                request.state.proxy_error = f"Internal error: {e}"
                last_error = str(e)
                status_code_for_error = 500
                self.unavailable_backends.add(backend.id)

        error_type = "Bad Gateway" if status_code_for_error == 502 else "Gateway Timeout" if status_code_for_error == 504 else "Internal Server Error"
        return JSONResponse(status_code=status_code_for_error, content={"error": error_type, "message": last_error or "All retries exhausted"})

proxy_service = ProxyService()
