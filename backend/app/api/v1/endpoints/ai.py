"""
AI 分析服务 API 端点

提供产品选品分析和关键词优化的 API 接口。
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import Optional
import logging
import os

from app.schemas.ai import (
    ProductSelectionRequest,
    ProductSelectionResponse,
    KeywordOptimizationRequest,
    KeywordOptimizationResponse,
    AIAnalysisError
)
from app.services.ai import ProductSelectionService, KeywordOptimizationService, DeepSeekClient
from app.services.sorftime import SorftimeClient

logger = logging.getLogger(__name__)

router = APIRouter()


# ==================== 依赖注入 ====================

def get_sorftime_client() -> SorftimeClient:
    """获取 Sorftime 客户端"""
    api_key = os.getenv("SORFTIME_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SORFTIME_API_KEY not configured"
        )
    return SorftimeClient(account_sk=api_key)


def get_deepseek_client() -> DeepSeekClient:
    """获取 DeepSeek 客户端"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="DEEPSEEK_API_KEY not configured"
        )
    return DeepSeekClient(api_key=api_key)


def get_product_selection_service(
    sorftime: SorftimeClient = Depends(get_sorftime_client),
    deepseek: DeepSeekClient = Depends(get_deepseek_client)
) -> ProductSelectionService:
    """获取产品选品服务"""
    return ProductSelectionService(sorftime, deepseek)


def get_keyword_optimization_service(
    sorftime: SorftimeClient = Depends(get_sorftime_client),
    deepseek: DeepSeekClient = Depends(get_deepseek_client)
) -> KeywordOptimizationService:
    """获取关键词优化服务"""
    return KeywordOptimizationService(sorftime, deepseek)


# ==================== API 端点 ====================

@router.post(
    "/product-selection",
    response_model=ProductSelectionResponse,
    summary="AI 产品选品分析",
    description="基于类目数据和 AI 分析，生成选品报告和建议",
    responses={
        200: {
            "description": "分析成功",
            "content": {
                "application/json": {
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
            }
        },
        400: {"description": "请求参数错误"},
        500: {"description": "服务器内部错误"}
    },
    tags=["AI Analysis"]
)
async def analyze_product_selection(
    request: ProductSelectionRequest,
    service: ProductSelectionService = Depends(get_product_selection_service)
):
    """
    AI 产品选品分析
    
    分析指定类目的市场机会，提供选品建议。
    
    **参数说明**:
    - category_id: 类目 ID (NodeId)，例如 "172282" 代表 Electronics
    - domain: 站点代码，1=美国，2=英国，3=德国，等
    - use_cache: 是否使用缓存，默认 true
    
    **返回内容**:
    - market_score: 市场机会评分 (1-10)
    - analysis: AI 生成的详细分析报告 (Markdown 格式)
    - statistics: 统计数据（平均价格、评分、评论数等）
    
    **注意事项**:
    - 首次分析可能需要 20-30 秒
    - 使用缓存可大幅提升响应速度
    - 建议在低峰期进行批量分析
    """
    try:
        logger.info(
            f"Received product selection request: "
            f"category_id={request.category_id}, domain={request.domain}"
        )
        
        # 调用服务进行分析
        result = await service.analyze_category(
            category_id=request.category_id,
            domain=request.domain,
            use_cache=request.use_cache
        )
        
        # 构建响应
        response = ProductSelectionResponse(
            category_id=result["category_id"],
            category_name=result["category_name"],
            domain=result["domain"],
            market_score=result["market_score"],
            analysis=result["analysis"],
            statistics=result["statistics"],
            timestamp=result["timestamp"]
        )
        
        logger.info(
            f"Product selection analysis completed: "
            f"category_id={request.category_id}, score={result['market_score']}"
        )
        
        return response
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in product selection analysis: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.post(
    "/keyword-optimization",
    response_model=KeywordOptimizationResponse,
    summary="AI 关键词优化",
    description="基于 ASIN 和关键词数据，生成优化后的 Listing",
    responses={
        200: {"description": "优化成功"},
        400: {"description": "请求参数错误"},
        500: {"description": "服务器内部错误"}
    },
    tags=["AI Analysis"]
)
async def optimize_keywords(
    request: KeywordOptimizationRequest,
    service: KeywordOptimizationService = Depends(get_keyword_optimization_service)
):
    """
    AI 关键词优化
    
    分析产品的关键词数据，生成优化后的标题、五点描述和后台搜索词。
    
    **参数说明**:
    - asin: 产品 ASIN，必须是 10 位字符，以 B 开头
    - domain: 站点代码
    - include_bullet_points: 是否包含五点描述优化
    - use_cache: 是否使用缓存
    
    **返回内容**:
    - optimized_title: 优化后的标题
    - optimization_report: 详细的优化报告 (Markdown 格式)
    
    **注意事项**:
    - 首次优化可能需要 15-20 秒
    - 优化建议仅供参考，请结合实际情况使用
    - 确保遵守 Amazon Listing 规范
    """
    try:
        logger.info(
            f"Received keyword optimization request: "
            f"asin={request.asin}, domain={request.domain}"
        )
        
        # 调用服务进行优化
        result = await service.optimize_listing(
            asin=request.asin,
            domain=request.domain,
            include_bullet_points=request.include_bullet_points,
            use_cache=request.use_cache
        )
        
        # 构建响应
        response = KeywordOptimizationResponse(
            asin=result["asin"],
            domain=result["domain"],
            original_title=result["original_title"],
            optimized_title=result["optimized_title"],
            optimization_report=result["optimization_report"],
            timestamp=result["timestamp"]
        )
        
        logger.info(
            f"Keyword optimization completed: asin={request.asin}"
        )
        
        return response
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in keyword optimization: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Optimization failed: {str(e)}"
        )


@router.get(
    "/health",
    summary="健康检查",
    description="检查 AI 服务是否正常运行",
    tags=["AI Analysis"]
)
async def health_check():
    """
    AI 服务健康检查
    
    检查 DeepSeek API 和 Sorftime API 的配置状态。
    """
    deepseek_configured = bool(os.getenv("DEEPSEEK_API_KEY"))
    sorftime_configured = bool(os.getenv("SORFTIME_API_KEY"))
    
    return {
        "status": "healthy" if (deepseek_configured and sorftime_configured) else "degraded",
        "services": {
            "deepseek": "configured" if deepseek_configured else "not_configured",
            "sorftime": "configured" if sorftime_configured else "not_configured"
        },
        "features": {
            "product_selection": deepseek_configured and sorftime_configured,
            "keyword_optimization": deepseek_configured and sorftime_configured
        }
    }
