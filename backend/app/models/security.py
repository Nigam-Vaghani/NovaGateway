import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base

class IPRule(Base):
    __tablename__ = "ip_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ip_cidr = Column(String, nullable=False, unique=True)
    rule_type = Column(String, nullable=False) # 'allow' or 'block'
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String, nullable=False, unique=True, index=True)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
