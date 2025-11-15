from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ExportRequest(BaseModel):
    export_type: str = Field(..., alias="exportType")
    filters: dict[str, Any] | None = None
    selected_fields: list[str] = Field(..., alias="selectedFields")
    file_format: str = Field("csv", alias="fileFormat")


class ExportJobOut(BaseModel):
    id: str
    export_type: str
    status: str
    file_format: str
    filters: dict | None
    selected_fields: list[str]
    file_path: str | None
    triggered_by: str | None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    error_message: str | None = None

    class Config:
        from_attributes = True
