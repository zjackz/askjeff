from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.models.system_log import SystemLog

LOG_LEVELS = ("debug", "info", "warning", "error")
SENSITIVE_KEYS = {"authorization", "token", "api_key", "password", "secret", "x-api-key"}


class LogService:
    """系统日志写入与查询。"""

    @staticmethod
    def log(
        db: Session,
        *,
        level: str,
        category: str,
        message: str,
        context: dict[str, Any] | None = None,
        trace_id: str | None = None,
    ) -> SystemLog:
        lvl = level.lower()
        if lvl not in LOG_LEVELS:
            raise ValueError("日志级别不合法")
        cleaned_context = LogService._sanitize(context or {})
        entry = SystemLog(
            id=str(uuid4()),
            timestamp=datetime.now(timezone.utc),
            level=lvl,
            category=category,
            message=message,
            context=cleaned_context or None,
            trace_id=trace_id,
            created_at=datetime.now(timezone.utc),
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry

    @staticmethod
    def list_logs(
        db: Session,
        *,
        level: str | None = None,
        category: str | None = None,
        keyword: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[SystemLog], int]:
        conditions = []
        if level:
            conditions.append(SystemLog.level == level.lower())
        if category:
            conditions.append(SystemLog.category == category)
        if keyword:
            conditions.append(
                SystemLog.message.ilike(f"%{keyword}%")
                | func.cast(SystemLog.context, sa.Text).ilike(f"%{keyword}%")
            )
        if start_time:
            conditions.append(SystemLog.timestamp >= start_time)
        if end_time:
            conditions.append(SystemLog.timestamp <= end_time)

        query_stmt = (
            select(SystemLog)
            .where(*conditions)
            .order_by(desc(SystemLog.timestamp))
            .limit(page_size)
            .offset((page - 1) * page_size)
        )
        count_stmt = select(func.count(SystemLog.id)).where(*conditions)

        rows = db.execute(query_stmt).scalars().all()
        total = db.execute(count_stmt).scalar_one()
        return rows, total

    @staticmethod
    def get_log(db: Session, log_id: str) -> SystemLog | None:
        stmt = select(SystemLog).where(SystemLog.id == log_id)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def fetch_by_ids(db: Session, ids: Iterable[str]) -> list[SystemLog]:
        stmt = select(SystemLog).where(SystemLog.id.in_(list(ids))).order_by(desc(SystemLog.timestamp))
        return db.execute(stmt).scalars().all()

    @staticmethod
    def _sanitize(context: dict[str, Any]) -> dict[str, Any]:
        """对敏感字段做脱敏，防止泄露密钥。"""
        sanitized: dict[str, Any] = {}
        for key, value in context.items():
            if isinstance(value, dict):
                sanitized[key] = LogService._sanitize(value)
                continue
            if key.lower() in SENSITIVE_KEYS:
                sanitized[key] = "***"
            else:
                sanitized[key] = value
        return sanitized
