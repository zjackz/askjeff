from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class ImportBatchOut(BaseModel):
    """导入批次输出模型，序列化为契约里的 camelCase 字段。"""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    filename: str
    import_strategy: str = Field(..., alias="importStrategy")
    status: str
    total_rows: int = Field(..., alias="totalRows")
    success_rows: int = Field(..., alias="successRows")
    failed_rows: int = Field(..., alias="failedRows")
    started_at: datetime | None = Field(default=None, alias="startedAt")
    finished_at: datetime | None = Field(default=None, alias="finishedAt")
    sheet_name: str | None = Field(default=None, alias="sheetName")
    failure_summary: dict | None = Field(default=None, alias="failureSummary")
    columns_seen: list[str] | None = Field(default=None, alias="columnsSeen")

    @field_serializer("id")
    def _serialize_id(self, value: str) -> str:
        return str(value)

    @field_serializer("import_strategy")
    def _serialize_strategy(self, value: str) -> str:
        return value.replace("_", "-")


class FailedRowOut(BaseModel):
    """失败行详情，便于前端直接渲染。"""

    model_config = ConfigDict(populate_by_name=True)

    row_number: int = Field(..., alias="rowNumber")
    asin: str | None = None
    reason: str
    raw_values: dict[str, Any] | None = Field(default=None, alias="rawValues")


class ImportDetailResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    batch: ImportBatchOut
    failed_rows: list[FailedRowOut] = Field(default_factory=list, alias="failedRows")


class ImportListResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: list[ImportBatchOut]
    total: int
