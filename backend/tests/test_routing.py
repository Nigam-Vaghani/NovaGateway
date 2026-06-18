import pytest
import asyncio
from app.routing_service import RoutingService
from app.models.routing import Route, Backend

@pytest.mark.asyncio
async def test_resolve_route_empty():
    routing_service = RoutingService()
    # Mock cache empty
    routing_service.routes_cache = []
    
    route, backends = await routing_service.resolve_route("/api/test")
    assert route is None
    assert backends == []

@pytest.mark.asyncio
async def test_resolve_route_match():
    routing_service = RoutingService()
    
    r1 = Route(id="1", path_prefix="/api", strip_prefix=True, is_active=True)
    b1 = Backend(id="b1", url="http://b1", route_id="1")
    
    routing_service.routes_cache = [r1]
    routing_service.backends_cache = {"1": [b1]}
    
    route, backends = await routing_service.resolve_route("/api/test")
    assert route is not None
    assert route.id == "1"
    assert len(backends) == 1
    assert backends[0].id == "b1"
