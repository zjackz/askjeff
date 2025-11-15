from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ImportBatchOut(BaseModel):
    id: str
    filename: str
    storage_path: str
    import_strategy: str
    status: str
    total_rows: int
    success_rows: int
    failed_rows: int
    started_at: datetime | None = None
    finished_at: datetime | None = None

    class Config:
        from_attributes = True


class ImportDetailResponse(BaseModel):
    batch: ImportBatchOut
    failure_summary: dict[str, Any] | None = None


class ImportListResponse(BaseModel):
    items: list[ImportBatchOut]
