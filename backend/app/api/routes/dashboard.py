from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services.audit_service import AuditService

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/activities")
async def get_recent_activities(
    limit: int = 10,
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    """获取最近的系统活动记录。"""
    logs = AuditService.get_recent_logs(db, limit=limit)
    return [
        {
            "id": log.id,
            "action": log.action,
            "actor_id": log.actor_id,
            "entity_id": log.entity_id,
            "payload": log.payload,
            "created_at": log.created_at,
        }
        for log in logs
    ]
