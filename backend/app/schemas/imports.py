from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class ImportBatchOut(BaseModel):
    """导入批次输出模型，序列化为契约里的 camelCase 字段。"""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
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
    
    # Added fields
    created_at: datetime = Field(..., alias="createdAt")
    created_by: str | None = Field(default=None, alias="createdBy")
    ai_status: str = Field(default="none", alias="aiStatus")
    ai_summary: dict | None = Field(default=None, alias="aiSummary")
    
    # Expose relative path for download
    storage_path: str = Field(..., alias="filePath")

    @field_serializer("storage_path")
    def _serialize_storage_path(self, value: str, _info) -> str:
        # Convert absolute path to relative path for API usage
        # e.g. /app/storage/imports/xxx.csv -> imports/xxx.csv
        # We look for the 'storage' directory in the path
        if "/storage/" in value:
            return value.split("/storage/")[-1]
        # Fallback for local dev where path might be different
        if "imports" in value:
             parts = value.split("/")
             try:
                 idx = parts.index("imports")
                 return "/".join(parts[idx:])
             except ValueError:
                 pass
        return value

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
