"""
AI 产品选品服务

基于 Sorftime API 数据和 DeepSeek AI，提供智能选品分析功能。
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import hashlib
import json

from app.services.sorftime import SorftimeClient
from app.services.ai.deepseek_client import DeepSeekClient
from app.services.ai.prompts import PromptTemplates

logger = logging.getLogger(__name__)


class ProductSelectionService:
    """
    AI 产品选品服务
    
    提供基于市场数据的智能选品分析，包括：
    - 类目市场分析
    - 产品潜力评估
    - 竞品对标分析
    - AI 生成选品报告
    """
    
    def __init__(
        self,
        sorftime_client: SorftimeClient,
        deepseek_client: DeepSeekClient
    ):
        """
        初始化选品服务
        
        Args:
            sorftime_client: Sorftime API 客户端
            deepseek_client: DeepSeek AI 客户端
        """
        self.sorftime = sorftime_client
        self.ai = deepseek_client
        self.prompts = PromptTemplates()
    
    async def analyze_category(
        self,
        category_id: str,
        domain: int = 1,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        分析类目选品机会
        
        Args:
            category_id: 类目 ID (NodeId)
            domain: 站点代码 (1=美国, 2=英国, 等)
            use_cache: 是否使用缓存
        
        Returns:
            包含分析结果的字典:
            {
                "category_id": str,
                "category_name": str,
                "market_score": float,
                "analysis": str,  # Markdown 格式
                "raw_data": dict,
                "timestamp": str
            }
        
        Raises:
            ValueError: 参数错误
            Exception: API 调用失败
        """
        logger.info(f"Starting category analysis: category_id={category_id}, domain={domain}")
        
        # 验证参数
        if not category_id:
            raise ValueError("category_id is required")
        
        # 1. 获取类目数据
        logger.info("Fetching category data from Sorftime API")
        category_data = await self._fetch_category_data(category_id, domain)
        
        # 2. 构建 AI Prompt
        logger.info("Building AI prompt")
        prompt = self._build_selection_prompt(category_data)
        
        # 3. 调用 AI 分析
        logger.info("Calling DeepSeek API for analysis")
        system_prompt = self.prompts.get_system_prompt("amazon_expert")
        analysis = await self.ai.analyze_with_system_prompt(
            system_prompt=system_prompt,
            user_prompt=prompt,
            temperature=0.7,
            max_tokens=4000
        )
        
        # 4. 解析结果
        market_score = self._extract_market_score(analysis)
        
        # 5. 构建返回结果
        result = {
            "category_id": category_id,
            "category_name": category_data.get("name", category_id),
            "domain": domain,
            "market_score": market_score,
            "analysis": analysis,
            "raw_data": category_data,
            "statistics": {
                "avg_price": category_data.get("avg_price"),
                "avg_rating": category_data.get("avg_rating"),
                "avg_reviews": category_data.get("avg_reviews"),
                "competition_level": category_data.get("competition_level", "中等")
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Analysis completed. Market score: {market_score}/10")
        return result
    
    async def _fetch_category_data(
        self,
        category_id: str,
        domain: int
    ) -> Dict[str, Any]:
        """
        获取类目相关数据
        
        从 Sorftime API 获取类目的 Best Sellers、趋势数据和产品详情。
        
        Args:
            category_id: 类目 ID
            domain: 站点代码
        
        Returns:
            聚合的类目数据
        """
        try:
            # 1. 获取类目 Best Sellers
            logger.info(f"Fetching category bestsellers: {category_id}")
            bestsellers_response = await self.sorftime.category_request(
                node_id=category_id,
                domain=domain
            )
            
            if bestsellers_response.code != 0:
                logger.error(f"Failed to fetch bestsellers: {bestsellers_response.message}")
                raise Exception(f"Sorftime API error: {bestsellers_response.message}")
            
            bestsellers = bestsellers_response.data if bestsellers_response.data else []
            
            # 2. 获取类目趋势数据
            logger.info(f"Fetching category trend: {category_id}")
            try:
                trend_response = await self.sorftime.category_trend(
                    node_id=category_id,
                    trend_index=0,  # 销量趋势
                    domain=domain
                )
                trend_data = trend_response.data if trend_response.code == 0 else None
            except Exception as e:
                logger.warning(f"Failed to fetch trend data: {str(e)}")
                trend_data = None
            
            # 3. 获取 Top 10 产品详情
            top_products = []
            if bestsellers and len(bestsellers) > 0:
                # 提取前 10 个产品的 ASIN
                asins = []
                for product in bestsellers[:10]:
                    asin = product.get('asin') or product.get('ASIN')
                    if asin:
                        asins.append(asin)
                
                if asins:
                    logger.info(f"Fetching product details for {len(asins)} ASINs")
                    try:
                        products_response = await self.sorftime.product_request(
                            asin=','.join(asins),
                            trend=0,  # 不需要趋势数据，节省时间
                            domain=domain
                        )
                        
                        if products_response.code == 0 and products_response.data:
                            # 确保返回的是列表
                            if isinstance(products_response.data, list):
                                top_products = products_response.data
                            else:
                                top_products = [products_response.data]
                    except Exception as e:
                        logger.warning(f"Failed to fetch product details: {str(e)}")
                        # 使用 bestsellers 中的基础数据
                        top_products = bestsellers[:10]
            
            # 4. 计算统计数据
            stats = self._calculate_statistics(top_products)
            
            # 5. 分析销量趋势
            sales_trend = self._analyze_sales_trend(trend_data)
            
            # 6. 评估竞争强度
            competition_level = self._assess_competition(top_products, stats)
            
            return {
                "name": category_id,  # TODO: 从 CategoryTree 获取实际名称
                "bestsellers": bestsellers[:20],  # 保留前 20 个
                "trend": trend_data,
                "sales_trend": sales_trend,
                "top_products": top_products,
                "avg_price": stats["avg_price"],
                "avg_rating": stats["avg_rating"],
                "avg_reviews": stats["avg_reviews"],
                "competition_level": competition_level,
                "total_products": len(bestsellers)
            }
            
        except Exception as e:
            logger.error(f"Error fetching category data: {str(e)}")
            raise
    
    def _calculate_statistics(self, products: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        计算产品统计数据
        
        Args:
            products: 产品列表
        
        Returns:
            统计数据字典
        """
        if not products:
            return {
                "avg_price": 0.0,
                "avg_rating": 0.0,
                "avg_reviews": 0
            }
        
        total_price = 0.0
        total_rating = 0.0
        total_reviews = 0
        valid_count = 0
        
        for product in products:
            # 价格
            price = product.get('price') or product.get('salesPrice') or 0
            if price and price > 0:
                total_price += float(price)
                valid_count += 1
            
            # 评分
            rating = product.get('ratings') or product.get('rating') or 0
            if rating:
                total_rating += float(rating)
            
            # 评论数
            reviews = product.get('ratingsCount') or product.get('reviewCount') or 0
            if reviews:
                total_reviews += int(reviews)
        
        count = len(products)
        
        return {
            "avg_price": round(total_price / valid_count, 2) if valid_count > 0 else 0.0,
            "avg_rating": round(total_rating / count, 1) if count > 0 else 0.0,
            "avg_reviews": int(total_reviews / count) if count > 0 else 0
        }
    
    def _analyze_sales_trend(self, trend_data: Optional[Any]) -> str:
        """
        分析销量趋势
        
        Args:
            trend_data: 趋势数据
        
        Returns:
            趋势描述文本
        """
        if not trend_data:
            return "趋势数据暂无"
        
        # TODO: 实现趋势分析逻辑
        # 这里简化处理，返回基本描述
        return "稳定增长"
    
    def _assess_competition(
        self, 
        products: List[Dict[str, Any]], 
        stats: Dict[str, float]
    ) -> str:
        """
        评估竞争强度
        
        基于评论数、评分等指标评估竞争强度。
        
        Args:
            products: 产品列表
            stats: 统计数据
        
        Returns:
            竞争强度: "低", "中等", "高"
        """
        avg_reviews = stats.get("avg_reviews", 0)
        avg_rating = stats.get("avg_rating", 0)
        
        # 简单的竞争强度评估逻辑
        if avg_reviews > 5000 and avg_rating > 4.5:
            return "高"
        elif avg_reviews > 1000 and avg_rating > 4.0:
            return "中等"
        else:
            return "低"
    
    def _build_selection_prompt(self, category_data: Dict[str, Any]) -> str:
        """
        构建选品分析 Prompt
        
        Args:
            category_data: 类目数据
        
        Returns:
            格式化的 Prompt
        """
        return self.prompts.product_selection_analysis(
            category_name=category_data.get("name", "未知类目"),
            sales_trend=category_data.get("sales_trend", "数据不足"),
            top_products=category_data.get("top_products", []),
            avg_price=category_data.get("avg_price", 0.0),
            avg_rating=category_data.get("avg_rating", 0.0),
            avg_reviews=category_data.get("avg_reviews", 0),
            competition_level=category_data.get("competition_level", "中等")
        )
    
    def _extract_market_score(self, analysis: str) -> float:
        """
        从 AI 分析结果中提取市场评分
        
        Args:
            analysis: AI 生成的分析文本
        
        Returns:
            市场评分 (1-10)
        """
        import re
        
        # 尝试匹配 "市场机会评分：X/10" 或 "市场机会评分：X.X/10"
        patterns = [
            r'市场机会评分[：:]\s*(\d+\.?\d*)\s*/\s*10',
            r'评分[：:]\s*(\d+\.?\d*)\s*/\s*10',
            r'(\d+\.?\d*)\s*/\s*10'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, analysis)
            if match:
                try:
                    score = float(match.group(1))
                    # 确保评分在 1-10 范围内
                    return max(1.0, min(10.0, score))
                except ValueError:
                    continue
        
        # 如果无法提取，返回默认值
        logger.warning("Could not extract market score from analysis, using default 5.0")
        return 5.0
    
    def generate_cache_key(self, category_id: str, domain: int) -> str:
        """
        生成缓存键
        
        Args:
            category_id: 类目 ID
            domain: 站点代码
        
        Returns:
            缓存键（MD5 哈希）
        """
        key_data = {
            "type": "product_selection",
            "category_id": category_id,
            "domain": domain
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
