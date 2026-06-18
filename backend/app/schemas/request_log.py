from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class RequestLogBase(BaseModel):
    client_ip: Optional[str] = None
    method: Optional[str] = None
    path: Optional[str] = None
    target_backend: Optional[str] = None
    status_code: Optional[int] = None
    latency_ms: Optional[float] = None
    response_size: Optional[int] = None
    error: Optional[str] = None
    cache_hit: Optional[bool] = False

class RequestLogCreate(RequestLogBase):
    pass

class RequestLogResponse(RequestLogBase):
    id: UUID
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

class PaginatedRequestLogsResponse(BaseModel):
    items: List[RequestLogResponse]
    total: int
    page: int
    size: int

class RequestsPerMinute(BaseModel):
    time: str
    requests: int

class StatusDistribution(BaseModel):
    name: str
    value: int

class TopEndpoint(BaseModel):
    path: str
    requests: int

class DashboardStatsResponse(BaseModel):
    totalRequests: int
    avgLatency: float
    errorRate: float
    cacheHitRate: float
    requestsPerMinute: List[RequestsPerMinute]
    statusDistribution: List[StatusDistribution]
    topEndpoints: List[TopEndpoint]
