from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse


class AppError(HTTPException):
    """统一业务异常，默认返回 400。"""

    def __init__(self, detail: str, status_code: int = 400) -> None:
        super().__init__(status_code=status_code, detail=detail)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"message": exc.detail})

    @app.exception_handler(Exception)
    async def handle_unexpected(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(status_code=500, content={"message": f\"系统异常: {exc}\"})
