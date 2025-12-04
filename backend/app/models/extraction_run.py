from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Enum, ForeignKey, Integer, Identity
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.utils.time import utc_now

if TYPE_CHECKING:
    from app.models.import_batch import ImportBatch

EXTRACTION_STATUS = ('pending', 'processing', 'completed', 'failed')

class ExtractionRun(Base):
    __tablename__ = 'extraction_runs'

    id: Mapped[int] = mapped_column(Integer, Identity(start=1), primary_key=True)
    batch_id: Mapped[int] = mapped_column(Integer, ForeignKey('import_batches.id'), nullable=False)
    
    status: Mapped[str] = mapped_column(Enum(*EXTRACTION_STATUS, name='extraction_status'), default='pending')
    target_fields: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    
    # Statistics
    stats: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    # Example stats structure:
    # {
    #   "total": 100,
    #   "success": 90,
    #   "failed": 10,
    #   "total_tokens": 5000,
    #   "input_tokens": 4000,
    #   "output_tokens": 1000,
    #   "total_cost": 0.05,
    #   "duration_seconds": 12.5
    # }

    created_at: Mapped[datetime] = mapped_column(default=utc_now)
    finished_at: Mapped[datetime | None] = mapped_column(nullable=True)

    batch: Mapped['ImportBatch'] = relationship('ImportBatch', back_populates='extraction_runs')
