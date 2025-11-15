from __future__ import annotations

from typing import Any
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


class AuditService:
    """统一的审计日志写入工具。"""

    @staticmethod
    def log_action(
        db: Session,
        *,
        action: str,
        actor_id: str | None = None,
        entity_id: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> AuditLog:
        log = AuditLog(
            id=str(uuid4()),
            actor_id=actor_id,
            action=action,
            entity_id=entity_id,
            payload=payload,
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
