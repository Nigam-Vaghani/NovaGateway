from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class BackendBase(BaseModel):
    url: str
    weight: Optional[int] = 1
    is_healthy: Optional[bool] = True

class BackendCreate(BackendBase):
    route_id: UUID

class BackendUpdate(BaseModel):
    url: Optional[str] = None
    weight: Optional[int] = None
    is_healthy: Optional[bool] = None

class BackendResponse(BackendBase):
    id: UUID
    route_id: UUID
    last_checked: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class RouteBase(BaseModel):
    name: str
    path_prefix: str
    strip_prefix: Optional[bool] = True
    is_active: Optional[bool] = True

class RouteCreate(RouteBase):
    pass

class RouteUpdate(BaseModel):
    name: Optional[str] = None
    path_prefix: Optional[str] = None
    strip_prefix: Optional[bool] = None
    is_active: Optional[bool] = None

class RouteResponse(RouteBase):
    id: UUID
    created_at: datetime
    backends: List[BackendResponse] = []

    model_config = ConfigDict(from_attributes=True)
