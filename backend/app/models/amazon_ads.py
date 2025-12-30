from datetime import date, datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

class AmazonStore(Base):
    """亚马逊店铺表 - 支持多店铺管理"""
    __tablename__ = "amazon_stores"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), index=True)
    
    # 店铺基本信息
    store_name: Mapped[str] = mapped_column(String(255))
    marketplace_id: Mapped[str] = mapped_column(String(20))  # ATVPDKIKX0DER (US), A1PA6795UKMFR9 (DE), etc.
    marketplace_name: Mapped[str] = mapped_column(String(50))  # United States, Germany, Japan, etc.
    seller_id: Mapped[str] = mapped_column(String(50))
    
    # API 凭证 (加密存储)
    sp_api_refresh_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    advertising_api_refresh_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 状态
    is_active: Mapped[bool] = mapped_column(default=True)
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('user_id', 'marketplace_id', 'seller_id', name='uix_user_marketplace_seller'),
    )

class ProductCost(Base):
    """产品成本表 (COGS) - 支持多店铺"""
    __tablename__ = "product_costs"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    store_id: Mapped[UUID] = mapped_column(ForeignKey('amazon_stores.id'), index=True)
    
    sku: Mapped[str] = mapped_column(String(100), index=True)
    asin: Mapped[str] = mapped_column(String(20), index=True)
    
    cogs: Mapped[float] = mapped_column(Float)  # Cost of Goods Sold
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    
    # 其他成本
    fba_fee: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    referral_fee_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 百分比
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('store_id', 'sku', name='uix_store_sku'),
    )

class InventorySnapshot(Base):
    """库存快照表 (每日) - 支持多店铺"""
    __tablename__ = "inventory_snapshots"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    store_id: Mapped[UUID] = mapped_column(ForeignKey('amazon_stores.id'), index=True)
    
    date: Mapped[date] = mapped_column(Date, index=True)
    sku: Mapped[str] = mapped_column(String(100), index=True)
    asin: Mapped[str] = mapped_column(String(20), index=True)
    
    # 库存数据
    fba_inventory: Mapped[int] = mapped_column(Integer, default=0)
    inbound_inventory: Mapped[int] = mapped_column(Integer, default=0)
    reserved_inventory: Mapped[int] = mapped_column(Integer, default=0)
    unfulfillable_inventory: Mapped[int] = mapped_column(Integer, default=0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('store_id', 'date', 'sku', name='uix_store_inventory_date_sku'),
    )

class AdsMetricSnapshot(Base):
    """广告指标快照表 (每日 SKU 粒度) - 支持多店铺"""
    __tablename__ = "ads_metric_snapshots"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    store_id: Mapped[UUID] = mapped_column(ForeignKey('amazon_stores.id'), index=True)
    
    date: Mapped[date] = mapped_column(Date, index=True)
    sku: Mapped[str] = mapped_column(String(100), index=True)
    asin: Mapped[str] = mapped_column(String(20), index=True)
    
    # 广告数据
    spend: Mapped[float] = mapped_column(Float, default=0.0)
    sales: Mapped[float] = mapped_column(Float, default=0.0)
    impressions: Mapped[int] = mapped_column(Integer, default=0)
    clicks: Mapped[int] = mapped_column(Integer, default=0)
    orders: Mapped[int] = mapped_column(Integer, default=0)
    units: Mapped[int] = mapped_column(Integer, default=0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('store_id', 'date', 'sku', name='uix_store_ads_date_sku'),
    )

class BusinessMetricSnapshot(Base):
    """业务指标快照表 (每日 SKU 粒度 - 销量/流量) - 支持多店铺"""
    __tablename__ = "business_metric_snapshots"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    store_id: Mapped[UUID] = mapped_column(ForeignKey('amazon_stores.id'), index=True)
    
    date: Mapped[date] = mapped_column(Date, index=True)
    sku: Mapped[str] = mapped_column(String(100), index=True)
    asin: Mapped[str] = mapped_column(String(20), index=True)
    
    # 业务数据
    total_sales_amount: Mapped[float] = mapped_column(Float, default=0.0)
    total_units_ordered: Mapped[int] = mapped_column(Integer, default=0)
    sessions: Mapped[int] = mapped_column(Integer, default=0)
    page_views: Mapped[int] = mapped_column(Integer, default=0)
    unit_session_percentage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('store_id', 'date', 'sku', name='uix_store_biz_date_sku'),
    )

