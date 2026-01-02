"""
Jeff Data Core 数据库模型

包含多租户支持、数据源管理、产品模型、
API 调用日志、同步任务、AI 调用日志、性能指标
"""

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import JSON, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from app.db import Base


TENANT_STATUS = ('active', 'suspended', 'cancelled')
SOURCE_TYPE = ('amazon_ads', 'amazon_sp', 'sorftime', 'shopify', 'file_import')
SYNC_TYPE = ('full_sync', 'incremental_sync')
SYNC_STATUS = ('pending', 'running', 'success', 'failed', 'cancelled')
API_METHOD = ('GET', 'POST', 'PUT', 'DELETE', 'PATCH')
API_STATUS = ('pending', 'running', 'success', 'failed')
AI_PROVIDER = ('deepseek', 'openai')
AI_FUNCTION = ('chat', 'extract_features', 'analyze', 'diagnose')


class JDC_Tenant(Base):
    """租户表"""
    __tablename__ = 'jdc_tenants'

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=False), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    api_key: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    status: Mapped[str] = mapped_column(Enum(*TENANT_STATUS, name='tenant_status'), default='active', index=True)
    
    # 配额限制
    max_api_calls_per_day: Mapped[int] = mapped_column(Integer, default=10000)
    max_ai_calls_per_day: Mapped[int] = mapped_column(Integer, default=1000)
    max_syncs_per_day: Mapped[int] = mapped_column(Integer, default=10)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    data_sources: Mapped[List['JDC_DataSource']] = relationship('JDC_DataSource', back_populates='tenant', cascade='all, delete-orphan')
    api_call_logs: Mapped[List['JDC_ApiCallLog']] = relationship('JDC_ApiCallLog', back_populates='tenant', cascade='all, delete-orphan')
    sync_tasks: Mapped[List['JDC_SyncTask']] = relationship('JDC_SyncTask', back_populates='tenant', cascade='all, delete-orphan')
    ai_call_logs: Mapped[List['JDC_AiCallLog']] = relationship('JDC_AiCallLog', back_populates='tenant', cascade='all, delete-orphan')
    performance_metrics: Mapped[List['JDC_PerformanceMetric']] = relationship('JDC_PerformanceMetric', back_populates='tenant', cascade='all, delete-orphan')
    products: Mapped[List['JDC_Product']] = relationship('JDC_Product', back_populates='tenant', cascade='all, delete-orphan')
    raw_data_logs: Mapped[List['JDC_RawDataLog']] = relationship('JDC_RawDataLog', back_populates='tenant', cascade='all, delete-orphan')


class JDC_DataSource(Base):
    """数据源配置表"""
    __tablename__ = 'jdc_data_sources'

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=False), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=False), ForeignKey('jdc_tenants.id', ondelete='CASCADE'), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    config: Mapped[dict] = mapped_column(JSONB, nullable=False)  # 具体配置
    is_active: Mapped[bool] = mapped_column(default=True, index=True)
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    sync_frequency: Mapped[str] = mapped_column(String(20), default='daily')  # hourly, daily, weekly

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    tenant: Mapped[JDC_Tenant] = relationship('JDC_Tenant', back_populates='data_sources')
    sync_tasks: Mapped[List['JDC_SyncTask']] = relationship('JDC_SyncTask', back_populates='data_source')

    __table_args__ = (
        {'schema': 'jdc'},
    )


class JDC_Product(Base):
    """统一产品表"""
    __tablename__ = 'jdc_products'

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=False), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=False), ForeignKey('jdc_tenants.id', ondelete='CASCADE'), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    source_id: Mapped[str] = mapped_column(String(100), index=True)  # 原始系统中的 ID

    # 产品基础信息
    asin: Mapped[Optional[str]] = mapped_column(String(20), index=True)
    sku: Mapped[Optional[str]] = mapped_column(String(100))
    title: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[Optional[str]] = mapped_column(Text)
    brand: Mapped[Optional[str]] = mapped_column(String(255))
    image_url: Mapped[Optional[str]] = mapped_column(Text)

    # 价格信息
    price: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3), default='USD')

    # 时间序列数据（每日快照）
    time_series: Mapped[dict] = mapped_column(JSONB, nullable=True)  # {"2025-01-01": {"sales": 100, "stock": 50}}

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    tenant: Mapped[JDC_Tenant] = relationship('JDC_Tenant', back_populates='products')

    __table_args__ = (
        {'schema': 'jdc'},
    )


class JDC_ApiCallLog(Base):
    """API 调用日志表"""
    __tablename__ = 'jdc_api_call_logs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=False), ForeignKey('jdc_tenants.id', ondelete='CASCADE'), nullable=False, index=True)
    api_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    endpoint: Mapped[str] = mapped_column(String(255), nullable=False)
    method: Mapped[str] = mapped_column(Enum(*API_METHOD, name='api_method'), nullable=False)

    # 请求信息
    request_id: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    request_body: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # 响应信息
    status_code: Mapped[Optional[int]] = mapped_column(Integer)
    response_time_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    response_body: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # 元数据
    success: Mapped[bool] = mapped_column(default=True, index=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, index=True)

    # 关系
    tenant: Mapped[JDC_Tenant] = relationship('JDC_Tenant', back_populates='api_call_logs')

    __table_args__ = (
        {'schema': 'jdc'},
    )


class JDC_SyncTask(Base):
    """数据同步任务表"""
    __tablename__ = 'jdc_sync_tasks'

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=False), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=False), ForeignKey('jdc_tenants.id', ondelete='CASCADE'), nullable=False, index=True)
    source_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=False), ForeignKey('jdc_data_sources.id', ondelete='CASCADE'), nullable=False, index=True)

    # 任务信息
    task_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[str] = mapped_column(Enum(*SYNC_STATUS, name='sync_status'), default='pending', index=True)

    # 时间信息
    start_time: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    end_time: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    estimated_duration_seconds: Mapped[Optional[int]] = mapped_column(Integer)

    # 同步统计
    records_total: Mapped[int] = mapped_column(Integer, default=0)
    records_success: Mapped[int] = mapped_column(Integer, default=0)
    records_failed: Mapped[int] = mapped_column(Integer, default=0)

    # 错误信息
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    error_details: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # 元数据
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, default=3)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, index=True)

    # 关系
    tenant: Mapped[JDC_Tenant] = relationship('JDC_Tenant', back_populates='sync_tasks')
    data_source: Mapped[JDC_DataSource] = relationship('JDC_DataSource', back_populates='sync_tasks')

    __table_args__ = (
        {'schema': 'jdc'},
    )


class JDC_AiCallLog(Base):
    """AI 调用日志表"""
    __tablename__ = 'jdc_ai_call_logs'

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=False), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=False), ForeignKey('jdc_tenants.id', ondelete='CASCADE'), nullable=False, index=True)
    ai_provider: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    model: Mapped[Optional[str]] = mapped_column(String(100))
    function_type: Mapped[str] = mapped_column(Enum(*AI_FUNCTION, name='ai_function'), nullable=False)

    # 输入输出
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    input_text: Mapped[Optional[str]] = mapped_column(Text)
    output_text: Mapped[Optional[str]] = mapped_column(Text)

    # 成本追踪
    cost_usd: Mapped[float] = mapped_column(Numeric(10, 4), default=0.0)
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)

    # 元数据
    response_time_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    success: Mapped[bool] = mapped_column(default=True, index=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, index=True)

    # 关系
    tenant: Mapped[JDC_Tenant] = relationship('JDC_Tenant', back_populates='ai_call_logs')

    __table_args__ = (
        {'schema': 'jdc'},
    )


class JDC_PerformanceMetric(Base):
    """性能指标表"""
    __tablename__ = 'jdc_performance_metrics'

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=False), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=False), ForeignKey('jdc_tenants.id', ondelete='CASCADE'), nullable=False, index=True)
    metric_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # 指标数据
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False)
    metric_value: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)
    unit: Mapped[Optional[str]] = mapped_column(String(20))

    # 时间窗口
    window_start: Mapped[datetime] = mapped_column(nullable=False, index=True)
    window_end: Mapped[datetime] = mapped_column(nullable=False)

    # 标签
    tags: Mapped[dict] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, index=True)

    # 关系
    tenant: Mapped[JDC_Tenant] = relationship('JDC_Tenant', back_populates='performance_metrics')

    __table_args__ = (
        {'schema': 'jdc'},
    )


class JDC_RawDataLog(Base):
    """原始数据日志表（用于调试）"""
    __tablename__ = 'jdc_raw_data_logs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=False), ForeignKey('jdc_tenants.id', ondelete='CASCADE'), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    data_type: Mapped[str] = mapped_column(String(50), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    meta_info: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, index=True)

    # 关系
    tenant: Mapped[JDC_Tenant] = relationship('JDC_Tenant', back_populates='raw_data_logs')

    __table_args__ = (
        {'schema': 'jdc'},
    )
