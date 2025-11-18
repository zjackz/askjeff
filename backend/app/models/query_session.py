from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base

SESSION_STATUS = ("succeeded", "failed")


class QuerySession(Base):
    __tablename__ = "query_sessions"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    question: Mapped[str] = mapped_column(Text, nullable=False)
    intent: Mapped[str | None] = mapped_column(Text, nullable=True)
    sql_template: Mapped[str | None] = mapped_column(Text, nullable=True)
    answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    references: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    deepseek_trace: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="succeeded")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    asked_by: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)
    asked_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
