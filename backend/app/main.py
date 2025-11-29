import time
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.errors import register_exception_handlers
from app.api.routes import (
    imports as imports_router,
    chat as chat_router,
    exports as exports_router,
    products as products_router,
    logs as logs_router,
    extraction as extraction_router,
)
from app.db import SessionLocal
from app.services.log_service import LogService

app = FastAPI(title="Sorftime 数据智能控制台 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)
app.include_router(imports_router.router)
app.include_router(chat_router.router)
app.include_router(exports_router.router)
app.include_router(products_router.router)
app.include_router(logs_router.router)
app.include_router(extraction_router.router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.middleware("http")
async def request_logging(request: Request, call_next):
    """记录请求耗时与状态，方便排障。"""
    trace_id = request.headers.get("X-Trace-Id", str(uuid4()))
    start = time.perf_counter()
    try:
        response = await call_next(request)
        status = response.status_code
        level = "warning" if status >= 400 else "info"
        duration = round((time.perf_counter() - start) * 1000, 2)
        with SessionLocal() as db:
            LogService.log(
                db,
                level=level,
                category="api_request",
                message=f"{request.method} {request.url.path}",
                context={
                    "status": status,
                    "duration_ms": duration,
                    "client": request.client.host if request.client else None,
                },
                trace_id=trace_id,
                status="info",
            )
        response.headers["X-Trace-Id"] = trace_id
        return response
    except Exception as exc:  # pragma: no cover - 防御
        duration = round((time.perf_counter() - start) * 1000, 2)
        with SessionLocal() as db:
            LogService.log(
                db,
                level="error",
                category="api_error",
                message=str(exc),
                context={
                    "path": request.url.path,
                    "method": request.method,
                    "duration_ms": duration,
                },
                trace_id=trace_id,
                status="new",
            )
        raise
