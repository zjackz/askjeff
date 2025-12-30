from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.errors import ErrorCode
from app.schemas.errors import ErrorDetail, ErrorResponse


class AppError(StarletteHTTPException):
    """统一业务异常,默认返回 400。
    
    注意: 此类保留用于向后兼容,新代码应使用 app.core.errors.AppException
    """

    def __init__(self, detail: str, status_code: int = 400) -> None:
        super().__init__(status_code=status_code, detail=detail)


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


def register_exception_handlers(app: FastAPI) -> None:
    """注册全局异常处理器"""

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """处理 HTTP 异常 (如 404, 405)"""
        trace_id = getattr(request.state, "trace_id", None)
        
        if exc.status_code == 404:
            details = {"path": str(request.url), "method": request.method}
            if trace_id:
                details["trace_id"] = trace_id
            
            # 如果是默认的 "Not Found"，则使用统一的中文提示
            # 否则（如业务逻辑抛出的特定 404），保留原始消息
            message = str(exc.detail)
            if message == "Not Found":
                message = f"请求的资源不存在: {request.url.path}"
                
            return create_error_response(
                code="RESOURCE_NOT_FOUND",
                message=message,
                details=details,
                status_code=404
            )
        
        details = {"trace_id": trace_id} if trace_id else None
        return create_error_response(
            code=f"HTTP_{exc.status_code}",
            message=str(exc.detail),
            details=details,
            status_code=exc.status_code
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """处理请求参数验证错误 (422)"""
        errors = []
        for error in exc.errors():
            # 获取字段路径
            loc = error.get("loc", [])
            field = ".".join(str(l) for l in loc) if loc else "unknown"
            
            errors.append({
                "field": field,
                "message": error.get("msg", "Invalid value"),
                "type": error.get("type", "value_error")
            })
            
        return create_error_response(
            code=ErrorCode.VALIDATION_ERROR,
            message="请求参数验证失败",
            details={"errors": errors},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
