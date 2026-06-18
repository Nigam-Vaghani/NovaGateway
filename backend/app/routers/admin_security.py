import secrets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.security import IPRule, APIKey
from app.schemas.security import IPRuleCreate, IPRuleResponse, APIKeyCreate, APIKeyResponse

router = APIRouter(prefix="/admin/security", tags=["Admin Security"])

@router.get("/ip-rules", response_model=List[IPRuleResponse])
async def get_ip_rules(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IPRule))
    return result.scalars().all()

@router.post("/ip-rules", response_model=IPRuleResponse)
async def create_ip_rule(rule: IPRuleCreate, db: AsyncSession = Depends(get_db)):
    db_rule = IPRule(**rule.model_dump())
    db.add(db_rule)
    try:
        await db.commit()
        await db.refresh(db_rule)
        return db_rule
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/ip-rules/{rule_id}")
async def delete_ip_rule(rule_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IPRule).where(IPRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    await db.delete(rule)
    await db.commit()
    return {"message": "Rule deleted"}

@router.get("/api-keys", response_model=List[APIKeyResponse])
async def get_api_keys(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(APIKey))
    return result.scalars().all()

@router.post("/api-keys", response_model=APIKeyResponse)
async def create_api_key(key_in: APIKeyCreate, db: AsyncSession = Depends(get_db)):
    raw_key = secrets.token_urlsafe(32)
    db_key = APIKey(name=key_in.name, key=raw_key)
    db.add(db_key)
    try:
        await db.commit()
        await db.refresh(db_key)
        return db_key
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/api-keys/{key_id}")
async def delete_api_key(key_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(APIKey).where(APIKey.id == key_id))
    key = result.scalar_one_or_none()
    if not key:
        raise HTTPException(status_code=404, detail="API Key not found")
    await db.delete(key)
    await db.commit()
    return {"message": "API Key deleted"}
