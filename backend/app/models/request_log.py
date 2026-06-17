import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base

class RequestLog(Base):
    __tablename__ = "request_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    client_ip = Column(String)
    method = Column(String)
    path = Column(String)
    target_backend = Column(String, nullable=True)
    status_code = Column(Integer, nullable=True)
    latency_ms = Column(Float, nullable=True)
    response_size = Column(Integer, nullable=True)
    error = Column(String, nullable=True)
    cache_hit = Column(Boolean, default=False)
