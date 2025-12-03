from __future__ import annotations

from datetime import datetime
from typing import List, TYPE_CHECKING
from uuid import uuid4

if TYPE_CHECKING:
    from app.models.extraction_run import ExtractionRun

from sqlalchemy import JSON, Enum, ForeignKey, Integer, Numeric, String, Text, Identity, FetchedValue
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.utils.time import utc_now

IMPORT_STATUS = ('pending', 'running', 'succeeded', 'failed')
IMPORT_STRATEGIES = ('overwrite', 'append', 'update_only')
VALIDATION_STATUS = ('valid', 'warning', 'error')


class ImportBatch(Base):
    __tablename__ = 'import_batches'

    id: Mapped[int] = mapped_column(Integer, Identity(start=1), primary_key=True)
    filename: Mapped[str] = mapped_column(Text, nullable=False)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    import_strategy: Mapped[str] = mapped_column(Enum(*IMPORT_STRATEGIES, name='import_strategy'), nullable=False)
    status: Mapped[str] = mapped_column(Enum(*IMPORT_STATUS, name='import_status'), default='pending')
    total_rows: Mapped[int] = mapped_column(Integer, default=0)
    success_rows: Mapped[int] = mapped_column(Integer, default=0)
    failed_rows: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime | None] = mapped_column(nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(nullable=True)
    sheet_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    failure_summary: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    columns_seen: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    
    # AI Extraction Status for the Batch
    ai_status: Mapped[str] = mapped_column(String(20), default='none') # none, pending, processing, completed, failed
    ai_summary: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
    archived: Mapped[bool] = mapped_column(default=False)

    records: Mapped[List['ProductRecord']] = relationship('ProductRecord', back_populates='batch', cascade='all, delete-orphan')
    extraction_runs: Mapped[List['ExtractionRun']] = relationship('ExtractionRun', back_populates='batch', cascade='all, delete-orphan')


class ProductRecord(Base):
    __tablename__ = 'product_records'

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    batch_id: Mapped[int] = mapped_column(Integer, ForeignKey('import_batches.id'), nullable=False)
    asin: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(3), nullable=True)
    sales_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reviews: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rating: Mapped[float | None] = mapped_column(Numeric(3, 2), nullable=True)
    raw_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    normalized_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    validation_status: Mapped[str] = mapped_column(Enum(*VALIDATION_STATUS, name='validation_status'), default='valid')
    validation_messages: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    # AI Extraction Fields
    ai_features: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ai_status: Mapped[str] = mapped_column(String(20), default='pending') # pending, success, failed
    
    ingested_at: Mapped[datetime] = mapped_column(default=utc_now)

    batch: Mapped[ImportBatch] = relationship('ImportBatch', back_populates='records')

    @property
    def batch_sequence_id(self) -> int | None:
        return self.batch.id if self.batch else None
