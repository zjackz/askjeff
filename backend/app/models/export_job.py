from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base

EXPORT_STATUS = ("pending", "running", "succeeded", "failed")
EXPORT_TYPES = ("clean_products", "failed_rows")
FILE_FORMATS = ("csv", "xlsx")


import uuid

class ExportJob(Base):
    __tablename__ = "export_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    export_type: Mapped[str] = mapped_column(String(32), nullable=False)
    filters: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    selected_fields: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    file_format: Mapped[str] = mapped_column(String(8), nullable=False, default="csv")
    status: Mapped[str] = mapped_column(String(32), default="pending")
    file_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(nullable=True)
    triggered_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
