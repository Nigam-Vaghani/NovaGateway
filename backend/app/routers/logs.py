from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from app.database import get_db
from app.models.request_log import RequestLog
from app.schemas.request_log import RequestLogResponse, PaginatedRequestLogsResponse, DashboardStatsResponse

router = APIRouter(prefix="/admin/logs", tags=["Logs"])

@router.get("", response_model=PaginatedRequestLogsResponse, summary="Get Request Logs", description="Retrieve paginated request logs with optional filtering by method, status, path, IP, and time range.")
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

@router.get("/{id}", response_model=RequestLogResponse, summary="Get Log Details", description="Retrieve a specific request log by its UUID.")
async def get_log(id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RequestLog).where(RequestLog.id == id))
    log_entry = result.scalar_one_or_none()
    
    if log_entry is None:
        raise HTTPException(status_code=404, detail="Log entry not found")
        
    return log_entry

@router.get("/dashboard/stats", response_model=DashboardStatsResponse, summary="Get Dashboard Statistics", description="Retrieve aggregated metrics and statistics for the past 24 hours.")
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    from datetime import timedelta
    now = datetime.utcnow()
    last_24h = now - timedelta(hours=24)
    last_60m = now - timedelta(minutes=60)

    # Total requests 24h
    res_total = await db.execute(select(func.count()).where(RequestLog.timestamp >= last_24h))
    total_24h = res_total.scalar() or 0

    # Avg Latency 24h
    res_lat = await db.execute(select(func.avg(RequestLog.latency_ms)).where(RequestLog.timestamp >= last_24h))
    avg_latency = float(res_lat.scalar() or 0)

    # Error Rate 24h (status >= 400)
    res_err = await db.execute(select(func.count()).where(RequestLog.timestamp >= last_24h, RequestLog.status_code >= 400))
    errors_24h = res_err.scalar() or 0
    error_rate = (errors_24h / total_24h * 100) if total_24h > 0 else 0

    # Cache hit rate 24h
    res_cache = await db.execute(select(func.count()).where(RequestLog.timestamp >= last_24h, RequestLog.cache_hit == True))
    cache_hits = res_cache.scalar() or 0
    cache_hit_rate = (cache_hits / total_24h * 100) if total_24h > 0 else 0

    # Requests per minute (last 60m)
    # Group by minute
    stmt_rpm = select(
        func.date_trunc('minute', RequestLog.timestamp).label('minute'),
        func.count().label('count')
    ).where(RequestLog.timestamp >= last_60m).group_by('minute').order_by('minute')
    
    res_rpm = await db.execute(stmt_rpm)
    rpm_data = [{"time": row.minute.strftime("%H:%M"), "requests": row.count} for row in res_rpm.all()]

    # Status distribution
    stmt_status = select(
        RequestLog.status_code,
        func.count().label('count')
    ).where(RequestLog.timestamp >= last_24h).group_by(RequestLog.status_code)
    
    res_status = await db.execute(stmt_status)
    status_data = [{"name": str(row.status_code), "value": row.count} for row in res_status.all()]

    # Top endpoints
    stmt_top = select(
        RequestLog.path,
        func.count().label('count')
    ).where(RequestLog.timestamp >= last_24h).group_by(RequestLog.path).order_by(func.count().desc()).limit(10)
    
    res_top = await db.execute(stmt_top)
    top_endpoints = [{"path": row.path, "requests": row.count} for row in res_top.all()]

    return {
        "totalRequests": total_24h,
        "avgLatency": round(avg_latency, 2),
        "errorRate": round(error_rate, 2),
        "cacheHitRate": round(cache_hit_rate, 2),
        "requestsPerMinute": rpm_data,
        "statusDistribution": status_data,
        "topEndpoints": top_endpoints
    }

