from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from app.database import get_db
from app.models.request_log import RequestLog
from app.schemas.request_log import RequestLogResponse, PaginatedRequestLogsResponse

router = APIRouter(prefix="/admin/logs", tags=["Logs"])

@router.get("", response_model=PaginatedRequestLogsResponse)
async def get_logs(
    method: Optional[str] = Query(None, description="Filter by HTTP method"),
    status_code: Optional[int] = Query(None, description="Filter by status code"),
    path: Optional[str] = Query(None, description="Filter by path (prefix match)"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    client_ip: Optional[str] = Query(None, description="Filter by client IP"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=1000, description="Items per page"),
    db: AsyncSession = Depends(get_db)
):
    query = select(RequestLog)
    
    if method:
        query = query.where(RequestLog.method == method)
    if status_code is not None:
        query = query.where(RequestLog.status_code == status_code)
    if path:
        query = query.where(RequestLog.path.startswith(path))
    if start_date:
        query = query.where(RequestLog.timestamp >= start_date)
    if end_date:
        query = query.where(RequestLog.timestamp <= end_date)
    if client_ip:
        query = query.where(RequestLog.client_ip == client_ip)
        
    # Count total items
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Get paginated items
    query = query.order_by(RequestLog.timestamp.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    items = result.scalars().all()
    
    return PaginatedRequestLogsResponse(
        items=items,
        total=total,
        page=page,
        size=page_size
    )

@router.get("/{id}", response_model=RequestLogResponse)
async def get_log(id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RequestLog).where(RequestLog.id == id))
    log_entry = result.scalar_one_or_none()
    
    if log_entry is None:
        raise HTTPException(status_code=404, detail="Log entry not found")
        
    return log_entry
