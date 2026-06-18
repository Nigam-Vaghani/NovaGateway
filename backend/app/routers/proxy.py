from fastapi import APIRouter, Request
from app.proxy_service import proxy_service

router = APIRouter(tags=["Proxy"])

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"], summary="Reverse Proxy Catch-All", description="Forwards incoming requests to the appropriate backend service based on configured routes.")
async def proxy_catch_all(request: Request, path: str):
    return await proxy_service.forward_request(request, path)
