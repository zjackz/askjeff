"""
AI 服务相关的 Pydantic Schemas

定义 AI 分析服务的请求和响应模型。
"""

from typing import Any

from pydantic import BaseModel, Field, validator


# ==================== 产品选品相关 ====================

class ProductSelectionRequest(BaseModel):
    """产品选品分析请求"""
    
    category_id: str = Field(
        ...,
        description="类目 ID (NodeId)",
        example="172282"
    )
    domain: int = Field(
        default=1,
        description="站点代码 (1=美国, 2=英国, 3=德国, 等)",
        ge=1,
        le=14
    )
    use_cache: bool = Field(
        default=True,
        description="是否使用缓存"
    )
    
    @validator('category_id')
    def validate_category_id(cls, v):
        if not v or not v.strip():
            raise ValueError("category_id 不能为空")
        return v.strip()


class ProductSelectionStatistics(BaseModel):
    """选品统计数据"""
    
    avg_price: float | None = Field(None, description="平均价格")
    avg_rating: float | None = Field(None, description="平均评分")
    avg_reviews: int | None = Field(None, description="平均评论数")
    competition_level: str | None = Field(None, description="竞争强度")


class ProductSelectionResponse(BaseModel):
    """产品选品分析响应"""
    
    category_id: str = Field(..., description="类目 ID")
    category_name: str = Field(..., description="类目名称")
    domain: int = Field(..., description="站点代码")
    market_score: float = Field(..., description="市场机会评分 (1-10)", ge=1.0, le=10.0)
    analysis: str = Field(..., description="AI 生成的分析报告 (Markdown 格式)")
    statistics: ProductSelectionStatistics = Field(..., description="统计数据")
    timestamp: str = Field(..., description="分析时间戳")
    
    class Config:
        json_schema_extra = {
            "example": {
                "category_id": "172282",
                "category_name": "Electronics",
                "domain": 1,
                "market_score": 8.5,
                "analysis": "## 市场机会评分：8.5/10\n\n### 市场分析\n...",
                "statistics": {
                    "avg_price": 45.99,
                    "avg_rating": 4.5,
                    "avg_reviews": 1250,
                    "competition_level": "中等"
                },
                "timestamp": "2024-12-17T06:30:00Z"
            }
        }


# ==================== 关键词优化相关 ====================

class KeywordOptimizationRequest(BaseModel):
    """关键词优化请求"""
    
    asin: str = Field(
        ...,
        description="产品 ASIN",
        example="B08N5WRWNW",
        min_length=10,
        max_length=10
    )
    domain: int = Field(
        default=1,
        description="站点代码",
        ge=1,
        le=14
    )
    include_bullet_points: bool = Field(
        default=True,
        description="是否包含五点描述优化"
    )
    use_cache: bool = Field(
        default=True,
        description="是否使用缓存"
    )
    
    @validator('asin')
    def validate_asin(cls, v):
        if not v or not v.strip():
            raise ValueError("ASIN 不能为空")
        v = v.strip().upper()
        if not v.startswith('B'):
            raise ValueError("ASIN 必须以 B 开头")
        if len(v) != 10:
            raise ValueError("ASIN 必须为 10 位")
        return v


class KeywordOptimizationResponse(BaseModel):
    """关键词优化响应"""
    
    asin: str = Field(..., description="产品 ASIN")
    domain: int = Field(..., description="站点代码")
    original_title: str = Field(..., description="原始标题")
    optimized_title: str = Field(..., description="优化后标题")
    optimization_report: str = Field(..., description="优化报告 (Markdown 格式)")
    timestamp: str = Field(..., description="优化时间戳")
    
    class Config:
        json_schema_extra = {
            "example": {
                "asin": "B08N5WRWNW",
                "domain": 1,
                "original_title": "Echo Dot (4th Gen) | Smart speaker...",
                "optimized_title": "Echo Dot 4th Gen Smart Speaker with Alexa...",
                "optimization_report": "## 优化后标题\n...",
                "timestamp": "2024-12-17T06:30:00Z"
            }
        }


# ==================== 通用响应 ====================

class AIAnalysisError(BaseModel):
    """AI 分析错误响应"""
    
    error: str = Field(..., description="错误类型")
    message: str = Field(..., description="错误消息")
    details: dict[str, Any] | None = Field(None, description="错误详情")


class AIAnalysisStatus(BaseModel):
    """AI 分析状态"""
    
    status: str = Field(..., description="状态: pending, processing, completed, failed")
    progress: int | None = Field(None, description="进度百分比 (0-100)")
    message: str | None = Field(None, description="状态消息")
    result: dict[str, Any] | None = Field(None, description="分析结果")


# ==================== 缓存相关 ====================

class CacheInfo(BaseModel):
    """缓存信息"""
    
    cache_key: str = Field(..., description="缓存键")
    hit: bool = Field(..., description="是否命中缓存")
    expires_at: str | None = Field(None, description="过期时间")
    created_at: str | None = Field(None, description="创建时间")
