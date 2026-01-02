"""
Jeff Data Core 认证和授权模块

支持多租户 API Key 认证
"""

import secrets
from typing import Optional
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.models.jdc_models import JDC_Tenant
from app.db import SessionLocal

logger = None


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class TenantAuthMiddleware:
    """租户认证中间件"""

    def __init__(self, api_key_header: str = "X-JDC-API-Key"):
        self.api_key_header = api_key_header

    async def __call__(self, request: Request, call_next):
        # 从 Header 获取 API Key
        api_key = request.headers.get(self.api_key_header)

        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing API Key",
                headers={"WWW-Authenticate": f"ApiKey realm=\"JDC\""}
            )

        # 验证 API Key
        db = SessionLocal()
        try:
            tenant = db.query(JDC_Tenant).filter(
                JDC_Tenant.api_key == api_key,
                JDC_Tenant.status == 'active'
            ).first()

            if not tenant:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid API Key"
                )

            # 将租户信息注入到 Request State
            request.state.tenant_id = str(tenant.id)
            request.state.tenant_name = tenant.name
            request.state.tenant_config = {
                'max_api_calls_per_day': tenant.max_api_calls_per_day,
                'max_ai_calls_per_day': tenant.max_ai_calls_per_day,
                'max_syncs_per_day': tenant.max_syncs_per_day
            }

        finally:
            db.close()

        response = await call_next(request)

        return response


async def get_current_tenant(request: Request) -> dict:
    """获取当前租户信息"""
    try:
        return {
            'tenant_id': request.state.tenant_id,
            'tenant_name': request.state.tenant_name,
            'config': request.state.tenant_config
        }
    except AttributeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tenant not authenticated"
        )


def generate_api_key(tenant_id: str) -> str:
    """生成 API Key"""
    api_key = f"jdc_{tenant_id}_{secrets.token_urlsafe(16)}"
    return api_key


def regenerate_api_key(db: Session, tenant_id: str) -> str:
    """重新生成 API Key"""
    tenant = db.query(JDC_Tenant).filter(JDC_Tenant.id == tenant_id).first()
    if not tenant:
        raise ValueError(f"Tenant not found: {tenant_id}")

    # 生成新的 API Key
    new_api_key = generate_api_key(tenant_id)

    # 更新数据库
    tenant.api_key = new_api_key
    db.commit()
    db.refresh(tenant)

    return new_api_key


def validate_api_key(db: Session, api_key: str) -> Optional[JDC_Tenant]:
    """验证 API Key"""
    tenant = db.query(JDC_Tenant).filter(
        JDC_Tenant.api_key == api_key,
        JDC_Tenant.status == 'active'
    ).first()

    return tenant


def check_rate_limit(request: Request, tenant_id: str, api_type: str) -> bool:
    """检查速率限制

    Args:
        request: FastAPI Request
        tenant_id: 租户 ID
        api_type: API 类型（'api' 或 'ai'）

    Returns:
        True 表示未超限，False 表示已超限
    """
    from datetime import datetime, timedelta

    config = request.state.tenant_config

    # 根据类型选择限制
    if api_type == 'api':
        max_calls = config['max_api_calls_per_day']
    elif api_type == 'ai':
        max_calls = config['max_ai_calls_per_day']
    else:
        max_calls = 100  # 默认限制

    # TODO: 实现基于 Redis 的速率限制
    # 这里先返回 True，实际使用 Redis 追踪调用次数

    return True
