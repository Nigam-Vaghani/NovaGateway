import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

class Route(Base):
    __tablename__ = "routes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    path_prefix = Column(String, nullable=False, unique=True)
    strip_prefix = Column(Boolean, default=True)
    require_api_key = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    cache_ttl_seconds = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    backends = relationship("Backend", back_populates="route", cascade="all, delete-orphan")

class Backend(Base):
    __tablename__ = "backends"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    route_id = Column(UUID(as_uuid=True), ForeignKey("routes.id", ondelete="CASCADE"), nullable=False)
    url = Column(String, nullable=False)
    weight = Column(Integer, default=1)
    is_healthy = Column(Boolean, default=True)
    last_checked = Column(DateTime(timezone=True), nullable=True)

    route = relationship("Route", back_populates="backends")
