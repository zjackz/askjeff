"""全局异常处理中间件

捕获所有未处理的异常并返回统一格式的错误响应
"""
from __future__ import annotations

import logging
import traceback
from typing import Callable

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.core.errors import AppException, ErrorCode, ERROR_MESSAGES
from app.schemas.errors import ErrorDetail, ErrorResponse

logger = logging.getLogger(__name__)


async def error_handler_middleware(request: Request, call_next: Callable) -> Response:
    """全局错误处理中间件"""
    try:
        response = await call_next(request)
        return response
    except AppException as exc:
        # 应用自定义异常
        logger.warning(
            f"AppException: {exc.code} - {exc.message}",
            extra={
                "code": exc.code,
                "path": request.url.path,
                "method": request.method,
                "details": exc.details
            }
        )
        return create_error_response(
            code=exc.code,
            message=exc.message,
            details=exc.details,
            status_code=exc.status_code
        )
    
    except ValidationError as exc:
        # Pydantic 验证错误
        logger.warning(f"ValidationError: {exc}", extra={"path": request.url.path})
        
        # 转换为用户友好的错误消息
        errors = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            errors.append({
                "field": field,
                "message": error["msg"],
                "type": error["type"]
            })
        
        return create_error_response(
            code=ErrorCode.VALIDATION_ERROR,
            message="请求参数验证失败",
            details={"errors": errors},
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    except SQLAlchemyError as exc:
        # 数据库错误
        logger.error(
            f"Database error: {exc}",
            extra={"path": request.url.path, "traceback": traceback.format_exc()}
        )
        return create_error_response(
            code=ErrorCode.DATABASE_ERROR,
            message=ERROR_MESSAGES[ErrorCode.DATABASE_ERROR],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    except Exception as exc:
        # 未知错误
        logger.error(
            f"Unhandled exception: {exc}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "traceback": traceback.format_exc()
            }
        )
        trace_id = getattr(request.state, "trace_id", None)
        details = {"trace_id": trace_id} if trace_id else None
        
        return create_error_response(
            code=ErrorCode.INTERNAL_SERVER_ERROR,
            message=ERROR_MESSAGES[ErrorCode.INTERNAL_SERVER_ERROR],
            details=details,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def create_error_response(
    code: str,
    message: str,
    details: dict | None = None,
    status_code: int = 400
) -> JSONResponse:
    """创建统一格式的错误响应"""
    error_response = ErrorResponse(
        error=ErrorDetail(
            code=code,
            message=message,
            details=details
        )
    )
    return JSONResponse(
        status_code=status_code,
        content=error_response.model_dump()
    )
