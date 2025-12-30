import time
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.errors import register_exception_handlers
from app.api.routes import (
    admin as admin_router,
    backups as backups_router,
    chat as chat_router,
    dashboard as dashboard_router,
    exports as exports_router,
    extraction as extraction_router,
    health as health_router,
    imports as imports_router,
    logs as logs_router,
    login as login_router,
    mcp as mcp_router,
    products as products_router,
    users as users_router,
)
from app.api.v1.endpoints import sorftime_test, ai
from app.db import SessionLocal
from app.services.log_service import LogService
from app.middleware.error_handler import error_handler_middleware

app = FastAPI(title="AskJeff API", version="0.1.0")

# 1. 日志中间件（最内层，记录原始请求和异常）
async def request_logging(request: Request, call_next):
    """记录请求耗时与状态，方便排障。"""
    trace_id = request.headers.get("X-Trace-Id", str(uuid4()))
    start = time.perf_counter()
    
    # 记录查询参数
    query_params = dict(request.query_params)
    
    try:
        response = await call_next(request)
        status = response.status_code
        level = "warning" if status >= 400 else "info"
        duration = round((time.perf_counter() - start) * 1000, 2)
        with SessionLocal() as db:
            LogService.log(
                db,
                level=level,
                category="api_call",
                message=f"{request.method} {request.url.path}",
                context={
                    "status": status,
                    "duration_ms": duration,
                    "client": request.client.host if request.client else None,
                    "query": query_params,
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
                category="api_call",
                message=str(exc),
                context={
                    "path": request.url.path,
                    "method": request.method,
                    "duration_ms": duration,
                    "query": query_params,
                },
                trace_id=trace_id,
                status="new",
            )
        raise

app.middleware("http")(request_logging)

# 2. 错误处理中间件 (中间层，捕获异常并转换为响应)
app.middleware("http")(error_handler_middleware)

# 3. CORS 配置 (最外层，确保所有响应都有 CORS 头)
# 注意: allow_credentials=True 时，allow_origins 不能为 ["*"]，必须指定具体域名
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5174",
        "http://localhost:3000",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局错误处理中间件已在上方注册（避免重复注册）
# app.middleware("http")(error_handler_middleware)  # 已移除重复注册

register_exception_handlers(app)

# 注册路由 - 统一使用 /api/v1 前缀
app.include_router(imports_router.router, prefix="/api/v1")
app.include_router(chat_router.router, prefix="/api/v1")
app.include_router(exports_router.router, prefix="/api/v1")
app.include_router(products_router.router, prefix="/api/v1")
app.include_router(logs_router.router, prefix="/api/v1")
app.include_router(users_router.router, prefix="/api/v1")
app.include_router(admin_router.router, prefix="/api/v1")
app.include_router(extraction_router.router, prefix="/api/v1")
app.include_router(dashboard_router.router, prefix="/api/v1")
app.include_router(mcp_router.router, prefix="/api/v1")
app.include_router(sorftime_test.router, prefix="/api/v1/sorftime", tags=["sorftime"])
app.include_router(ai.router, prefix="/api/v1/ai", tags=["AI Analysis"])

# 健康检查和登录路由 (使用 /api 前缀,但不使用 /v1)
app.include_router(health_router.router, prefix="/api", tags=["health"])
app.include_router(login_router.router, prefix="/api", tags=["login"])
app.include_router(backups_router.router, prefix="/api/v1/backups", tags=["backups"])
