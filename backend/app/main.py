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
    # amazon as amazon_router,  # 暂时注释,缺少 requests 依赖
)
from app.api.v1.endpoints import sorftime_test, ai, ads_analysis, amazon_sync, amazon_ads, data_engine, stores
from app.db import SessionLocal
from app.services.log_service import LogService
from app.middleware.error_handler import error_handler_middleware

app = FastAPI(title="AskJeff API", version="0.1.0")

# ... (middleware setup) ...
# Re-adding CORS just in case, as it seems missing in the view
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
app.include_router(ads_analysis.router, prefix="/api/v1/ads-analysis", tags=["Ads Analysis"])
app.include_router(amazon_sync.router, prefix="/api/v1/amazon", tags=["Amazon Sync"])
app.include_router(amazon_ads.router, prefix="/api/v1/amazon", tags=["Amazon Ads"])
app.include_router(data_engine.router, prefix="/api/v1/data", tags=["Data Engine"])
app.include_router(stores.router, prefix="/api/v1/stores", tags=["Store Management"])

# 健康检查和登录路由 (使用 /api 前缀,但不使用 /v1)
app.include_router(health_router.router, prefix="/api", tags=["health"])
app.include_router(login_router.router, prefix="/api/v1", tags=["login"])
app.include_router(backups_router.router, prefix="/api/v1/backups", tags=["backups"])
# app.include_router(amazon_router.router, prefix="/api/v1/amazon", tags=["Amazon"])
