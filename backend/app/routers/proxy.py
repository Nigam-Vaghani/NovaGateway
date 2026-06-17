from fastapi import APIRouter, Request
from app.proxy_service import proxy_service

router = APIRouter()

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"])
async def proxy_catch_all(request: Request, path: str):
    return await proxy_service.forward_request(request, path)
