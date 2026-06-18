from fastapi import APIRouter
from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str
    version: str

router = APIRouter(tags=["System"])

@router.get("/health", summary="System Health Check", description="Returns the current health status and version of the NovaGateway API.", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="ok", version="1.0.0")
