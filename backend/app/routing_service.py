import logging
from typing import Optional, Tuple, List
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import AsyncSessionLocal
from app.models.routing import Route, Backend

logger = logging.getLogger(__name__)

class RoutingService:
    async def resolve_route(self, path: str) -> Tuple[Optional[Route], List[Backend]]:
        async with AsyncSessionLocal() as session:
            # Get all routes, and their backends
            stmt = select(Route).options(selectinload(Route.backends))
            result = await session.execute(stmt)
            routes = result.scalars().all()

            # Find longest matching path_prefix
            matched_route = None
            max_len = -1
            
            # ensure path starts with / for matching
            search_path = f"/{path}" if not path.startswith("/") else path
            if search_path == "/":
                search_path = "" # Handle root
            
            # Simple prefix matching for now
            # path: /api/v1/users -> match /api/v1
            for route in routes:
                prefix = route.path_prefix
                if search_path.startswith(prefix) or (prefix == "/" and search_path == ""):
                    if len(prefix) > max_len:
                        matched_route = route
                        max_len = len(prefix)

            if not matched_route:
                return None, []

            # Filter healthy backends
            healthy_backends = [b for b in matched_route.backends if b.is_healthy]
            
            return matched_route, healthy_backends

routing_service = RoutingService()
