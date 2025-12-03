from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field, ConfigDict


class ErrorDetail(BaseModel):
    """错误详情"""
    code: str = Field(..., description="错误码,如 VALIDATION_ERROR")
    message: str = Field(..., description="用户友好的错误消息")
    details: Optional[dict[str, Any]] = Field(None, description="详细错误信息")


class ErrorResponse(BaseModel):
    """统一错误响应格式"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "文件格式不正确",
                    "details": {
                        "field": "file",
                        "reason": "仅支持 CSV 和 XLSX 格式"
                    }
                }
            }
        }
    )
    
    error: ErrorDetail
