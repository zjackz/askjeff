import uuid
from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db import Base

class ExtractionTask(Base):
    __tablename__ = "extraction_tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), default="PENDING", nullable=False
    )  # PENDING, PROCESSING, COMPLETED, FAILED
    target_fields: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    items: Mapped[List["ExtractionItem"]] = relationship(
        "ExtractionItem", back_populates="task", cascade="all, delete-orphan"
    )


class ExtractionItem(Base):
    __tablename__ = "extraction_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("extraction_tasks.id"), nullable=False, index=True
    )
    
    original_data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    extracted_data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=True)
    
    status: Mapped[str] = mapped_column(
        String(50), default="PENDING", nullable=False
    )  # PENDING, SUCCESS, FAILED
    
    error_message: Mapped[str] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    task: Mapped["ExtractionTask"] = relationship("ExtractionTask", back_populates="items")
