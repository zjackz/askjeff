from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse


class AppError(HTTPException):
    """统一业务异常,默认返回 400。
    
    注意: 此类保留用于向后兼容,新代码应使用 app.core.errors.AppException
    """

    def __init__(self, detail: str, status_code: int = 400) -> None:
        super().__init__(status_code=status_code, detail=detail)


def register_exception_handlers(app: FastAPI) -> None:
    """注册异常处理器
    
    注意: 全局错误处理已由 error_handler_middleware 统一处理,
    此函数保留用于向后兼容,实际不再注册额外的处理器。
    所有异常都会被中间件捕获并返回统一格式: {error:{code,message,details}}
    """
    pass
