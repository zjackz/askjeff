from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

LOG_LEVELS = {"debug", "info", "warning", "error"}
LOG_CATEGORIES = {"api_request", "api_error", "import", "export", "chat", "system", "frontend"}


class SystemLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    timestamp: datetime
    level: str
    category: str
    message: str
    context: dict[str, Any] | None = None
    trace_id: str | None = Field(default=None, alias="traceId")
    status: str = "new"
    resolved_by: str | None = Field(default=None, alias="resolvedBy")
    resolved_at: datetime | None = Field(default=None, alias="resolvedAt")
    resolution_note: str | None = Field(default=None, alias="resolutionNote")


class LogListResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: list[SystemLogOut]
    total: int


class LogIngestRequest(BaseModel):
    """客户端提交错误/事件日志。"""

    level: str = Field(default="error")
    category: str = Field(default="frontend")
    message: str
    context: dict[str, Any] | None = None
    trace_id: str | None = Field(default=None, alias="traceId")


class LogAnalyzeRequest(BaseModel):
    """日志分析请求，支持传 logIds 或筛选参数。"""

    log_ids: list[str] | None = Field(default=None, alias="logIds")
    level: str | None = None
    category: str | None = None
    keyword: str | None = None
    limit: int = Field(default=50, ge=1, le=200)


class LogAnalyzeResult(BaseModel):
    summary: str
    probable_causes: list[str] = Field(alias="probableCauses")
    suggestions: list[str]
    used_ai: bool = Field(alias="usedAi")
