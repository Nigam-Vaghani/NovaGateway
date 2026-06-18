from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel
from typing import Dict, Any

from app.cache_service import cache_service

router = APIRouter(prefix="/admin/cache", tags=["Admin Cache"])

class InvalidateRequest(BaseModel):
    pattern: str

@router.post("/invalidate")
async def invalidate_cache(request: InvalidateRequest):
    if not request.pattern:
        raise HTTPException(status_code=400, detail="Pattern is required")
    await cache_service.invalidate(request.pattern)
    return {"status": "success", "message": f"Invalidated cache matching pattern: {request.pattern}"}

@router.get("/stats")
async def get_cache_stats() -> Dict[str, Any]:
    stats = await cache_service.get_stats()
    return stats
