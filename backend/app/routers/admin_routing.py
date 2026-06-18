from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.routing import Route, Backend
from app.schemas.routing import (
    RouteCreate, RouteUpdate, RouteResponse,
    BackendCreate, BackendUpdate, BackendResponse
)

router = APIRouter(prefix="/admin", tags=["admin_routing"])

# ROUTES
@router.get("/routes", response_model=List[RouteResponse])
async def get_routes(db: AsyncSession = Depends(get_db)):
    stmt = select(Route).options(selectinload(Route.backends))
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/routes", response_model=RouteResponse)
async def create_route(route: RouteCreate, db: AsyncSession = Depends(get_db)):
    from sqlalchemy.exc import IntegrityError
    db_route = Route(**route.model_dump())
    db.add(db_route)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Route with this path prefix already exists")
    
    stmt = select(Route).where(Route.id == db_route.id).options(selectinload(Route.backends))
    result = await db.execute(stmt)
    return result.scalar_one()

@router.get("/routes/{id}", response_model=RouteResponse)
async def get_route(id: UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(Route).where(Route.id == id).options(selectinload(Route.backends))
    result = await db.execute(stmt)
    db_route = result.scalar_one_or_none()
    if not db_route:
        raise HTTPException(status_code=404, detail="Route not found")
    return db_route

@router.put("/routes/{id}", response_model=RouteResponse)
async def update_route(id: UUID, route: RouteUpdate, db: AsyncSession = Depends(get_db)):
    stmt = select(Route).where(Route.id == id).options(selectinload(Route.backends))
    result = await db.execute(stmt)
    db_route = result.scalar_one_or_none()
    if not db_route:
        raise HTTPException(status_code=404, detail="Route not found")
    
    update_data = route.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_route, key, value)
    
    await db.commit()
    await db.refresh(db_route)
    return db_route

@router.delete("/routes/{id}")
async def delete_route(id: UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(Route).where(Route.id == id)
    result = await db.execute(stmt)
    db_route = result.scalar_one_or_none()
    if not db_route:
        raise HTTPException(status_code=404, detail="Route not found")
    
    await db.delete(db_route)
    await db.commit()
    return {"message": "Route deleted"}

@router.patch("/routes/{id}/toggle", response_model=RouteResponse)
async def toggle_route(id: UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(Route).where(Route.id == id).options(selectinload(Route.backends))
    result = await db.execute(stmt)
    db_route = result.scalar_one_or_none()
    if not db_route:
        raise HTTPException(status_code=404, detail="Route not found")
    
    db_route.is_active = not db_route.is_active
    await db.commit()
    await db.refresh(db_route)
    return db_route

# BACKENDS
@router.get("/backends", response_model=List[BackendResponse])
async def get_backends(db: AsyncSession = Depends(get_db)):
    stmt = select(Backend)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/backends", response_model=BackendResponse)
async def create_backend(backend: BackendCreate, db: AsyncSession = Depends(get_db)):
    stmt = select(Route).where(Route.id == backend.route_id)
    result = await db.execute(stmt)
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Route not found")
        
    db_backend = Backend(**backend.model_dump())
    db.add(db_backend)
    await db.commit()
    await db.refresh(db_backend)
    return db_backend

@router.get("/backends/{id}", response_model=BackendResponse)
async def get_backend(id: UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(Backend).where(Backend.id == id)
    result = await db.execute(stmt)
    db_backend = result.scalar_one_or_none()
    if not db_backend:
        raise HTTPException(status_code=404, detail="Backend not found")
    return db_backend

@router.put("/backends/{id}", response_model=BackendResponse)
async def update_backend(id: UUID, backend: BackendUpdate, db: AsyncSession = Depends(get_db)):
    stmt = select(Backend).where(Backend.id == id)
    result = await db.execute(stmt)
    db_backend = result.scalar_one_or_none()
    if not db_backend:
        raise HTTPException(status_code=404, detail="Backend not found")
    
    update_data = backend.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_backend, key, value)
    
    await db.commit()
    await db.refresh(db_backend)
    return db_backend

@router.delete("/backends/{id}")
async def delete_backend(id: UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(Backend).where(Backend.id == id)
    result = await db.execute(stmt)
    db_backend = result.scalar_one_or_none()
    if not db_backend:
        raise HTTPException(status_code=404, detail="Backend not found")
    
    await db.delete(db_backend)
    await db.commit()
    return {"message": "Backend deleted"}

@router.patch("/backends/{id}/toggle", response_model=BackendResponse)
async def toggle_backend(id: UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(Backend).where(Backend.id == id)
    result = await db.execute(stmt)
    db_backend = result.scalar_one_or_none()
    if not db_backend:
        raise HTTPException(status_code=404, detail="Backend not found")
    
    db_backend.is_healthy = not db_backend.is_healthy
    await db.commit()
    await db.refresh(db_backend)
    return db_backend
