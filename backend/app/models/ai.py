"""
AI 分析相关的数据库模型

用于存储 AI 生成的选品报告和关键词优化记录。
"""

import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db import Base


class ProductSelectionReport(Base):
    """
    产品选品报告
    
    存储 AI 生成的选品分析报告，包括市场评分、详细分析和推荐建议。
    """
    __tablename__ = "product_selection_reports"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    
    # 类目信息
    category_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    category_name: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[int] = mapped_column(Integer, nullable=False, default=1)  # 站点代码
    
    # 分析结果
    market_score: Mapped[float] = mapped_column(Float, nullable=False)  # 市场机会评分 1-10
    analysis: Mapped[str] = mapped_column(Text, nullable=False)  # AI 生成的 Markdown 报告
    
    # 原始数据（用于审计和重新分析）
    raw_data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=True)
    
    # 统计数据
    avg_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    avg_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    avg_reviews: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    competition_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # 元数据
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    
    # 用户关联（可选，用于多用户场景）
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True
    )
    
    def __repr__(self) -> str:
        return f"<ProductSelectionReport(id={self.id}, category={self.category_name}, score={self.market_score})>"


class KeywordOptimization(Base):
    """
    关键词优化记录
    
    存储 AI 生成的关键词优化建议，包括标题、五点描述和后台搜索词。
    """
    __tablename__ = "keyword_optimizations"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    
    # 产品信息
    asin: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    domain: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    category: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # 原始内容
    original_title: Mapped[str] = mapped_column(Text, nullable=False)
    original_bullet_points: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # 优化后内容
    optimized_title: Mapped[str] = mapped_column(Text, nullable=False)
    optimized_bullet_points: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    backend_keywords: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # AI 分析报告
    optimization_report: Mapped[str] = mapped_column(Text, nullable=False)  # Markdown 格式
    
    # 关键词数据
    keywords_data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=True)
    
    # 元数据
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    
    # 用户关联
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True
    )
    
    def __repr__(self) -> str:
        return f"<KeywordOptimization(id={self.id}, asin={self.asin})>"


class AIAnalysisCache(Base):
    """
    AI 分析缓存
    
    用于缓存 AI 分析结果，避免重复调用 API。
    """
    __tablename__ = "ai_analysis_cache"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    
    # 缓存键（基于输入参数生成的哈希）
    cache_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    
    # 分析类型
    analysis_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # product_selection, keyword_optimization, competitor_analysis
    
    # 输入参数
    input_params: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    
    # 分析结果
    result: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    
    # 缓存元数据
    hit_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 命中次数
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)  # 过期时间
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_accessed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    
    def __repr__(self) -> str:
        return f"<AIAnalysisCache(id={self.id}, type={self.analysis_type}, hits={self.hit_count})>"
