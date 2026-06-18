from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime
from typing import Optional

class IPRuleBase(BaseModel):
    ip_cidr: str
    rule_type: str = Field(pattern="^(allow|block)$")

class IPRuleCreate(IPRuleBase):
    pass

class IPRuleResponse(IPRuleBase):
    id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class APIKeyBase(BaseModel):
    name: str

class APIKeyCreate(APIKeyBase):
    pass

class APIKeyResponse(APIKeyBase):
    id: UUID
    key: str
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
