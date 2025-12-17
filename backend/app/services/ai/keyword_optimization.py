"""
AI 关键词优化服务

基于 Sorftime API 数据和 DeepSeek AI，提供智能关键词优化功能。
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


class KeywordOptimizationService:
    """
    AI 关键词优化服务
    
    提供基于关键词数据的智能 Listing 优化，包括：
    - 关键词挖掘（反查竞品、类目关键词）
    - Listing 优化（标题、五点、后台词）
    - 效果追踪（排名监控、流量分析）
    """
    
    def __init__(
        self,
        sorftime_client: SorftimeClient,
        deepseek_client: DeepSeekClient
    ):
        """
        初始化关键词优化服务
        
        Args:
            sorftime_client: Sorftime API 客户端
            deepseek_client: DeepSeek AI 客户端
        """
        self.sorftime = sorftime_client
        self.ai = deepseek_client
        self.prompts = PromptTemplates()
    
    async def optimize_listing(
        self,
        asin: str,
        domain: int = 1,
        include_bullet_points: bool = True,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        优化产品 Listing
        
        Args:
            asin: 产品 ASIN
            domain: 站点代码
            include_bullet_points: 是否包含五点描述优化
            use_cache: 是否使用缓存
        
        Returns:
            包含优化结果的字典:
            {
                "asin": str,
                "domain": int,
                "original_title": str,
                "optimized_title": str,
                "optimization_report": str,  # Markdown 格式
                "timestamp": str
            }
        
        Raises:
            ValueError: 参数错误
            Exception: API 调用失败
        """
        logger.info(f"Starting keyword optimization: asin={asin}, domain={domain}")
        
        # 验证参数
        if not asin or len(asin) != 10:
            raise ValueError("Invalid ASIN format")
        
        # 1. 获取关键词数据
        logger.info("Fetching keyword data from Sorftime API")
        keyword_data = await self._fetch_keyword_data(asin, domain)
        
        # 2. 构建 AI Prompt
        logger.info("Building AI prompt for keyword optimization")
        prompt = self._build_optimization_prompt(keyword_data, include_bullet_points)
        
        # 3. 调用 AI 优化
        logger.info("Calling DeepSeek API for optimization")
        system_prompt = self.prompts.get_system_prompt("seo_specialist")
        optimization_report = await self.ai.analyze_with_system_prompt(
            system_prompt=system_prompt,
            user_prompt=prompt,
            temperature=0.7,
            max_tokens=4000
        )
        
        # 4. 解析优化结果
        optimized_title = self._extract_optimized_title(optimization_report)
        
        # 5. 构建返回结果
        result = {
            "asin": asin,
            "domain": domain,
            "original_title": keyword_data.get("current_title", ""),
            "optimized_title": optimized_title,
            "optimization_report": optimization_report,
            "keywords_data": {
                "core_keywords": keyword_data.get("core_keywords", [])[:10],
                "competitor_keywords": keyword_data.get("competitor_keywords", [])[:10],
                "long_tail_keywords": keyword_data.get("long_tail_keywords", [])[:10]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Optimization completed for ASIN: {asin}")
        return result
    
    async def _fetch_keyword_data(
        self,
        asin: str,
        domain: int
    ) -> Dict[str, Any]:
        """
        获取关键词相关数据
        
        从 Sorftime API 获取产品信息和关键词数据。
        
        Args:
            asin: 产品 ASIN
            domain: 站点代码
        
        Returns:
            聚合的关键词数据
        """
        try:
            # 1. 获取产品基本信息（包含当前标题）
            logger.info(f"Fetching product info for ASIN: {asin}")
            product_response = await self.sorftime.product_request(
                asin=asin,
                trend=0,  # 不需要趋势数据
                domain=domain
            )
            
            if product_response.code != 0:
                logger.error(f"Failed to fetch product info: {product_response.message}")
                raise Exception(f"Sorftime API error: {product_response.message}")
            
            product_data = product_response.data
            if isinstance(product_data, list):
                product_data = product_data[0] if product_data else {}
            
            current_title = product_data.get('title', '')
            category = product_data.get('category', ['Unknown'])[0] if product_data.get('category') else 'Unknown'
            current_bullet_points = product_data.get('Feature', [])
            
            # 2. 反查 ASIN 关键词
            logger.info(f"Fetching ASIN keywords: {asin}")
            core_keywords = []
            try:
                asin_keywords_response = await self.sorftime.asin_request_keyword(
                    asin=asin,
                    page=1,
                    domain=domain
                )
                
                if asin_keywords_response.code == 0 and asin_keywords_response.data:
                    # 提取关键词列表
                    keywords_data = asin_keywords_response.data
                    if isinstance(keywords_data, dict):
                        # 假设数据格式为 {"keywords": [...]}
                        core_keywords = keywords_data.get('keywords', [])
                    elif isinstance(keywords_data, list):
                        core_keywords = keywords_data
                    
                    # 提取关键词文本
                    core_keywords = self._extract_keyword_texts(core_keywords)
            except Exception as e:
                logger.warning(f"Failed to fetch ASIN keywords: {str(e)}")
            
            # 3. 获取类目关键词（如果有类目信息）
            competitor_keywords = []
            if category and category != 'Unknown':
                logger.info(f"Fetching category keywords for: {category}")
                try:
                    # 这里需要 category node_id，暂时跳过
                    # 实际使用中需要先通过 CategoryTree 获取 node_id
                    pass
                except Exception as e:
                    logger.warning(f"Failed to fetch category keywords: {str(e)}")
            
            # 4. 生成长尾关键词（基于核心词组合）
            long_tail_keywords = self._generate_long_tail_keywords(core_keywords)
            
            # 5. 如果没有获取到关键词，使用标题中的词作为备选
            if not core_keywords and current_title:
                core_keywords = self._extract_keywords_from_title(current_title)
            
            return {
                "asin": asin,
                "current_title": current_title,
                "category": category,
                "current_bullet_points": current_bullet_points,
                "core_keywords": core_keywords[:20],  # 保留前 20 个
                "competitor_keywords": competitor_keywords[:20],
                "long_tail_keywords": long_tail_keywords[:15]
            }
            
        except Exception as e:
            logger.error(f"Error fetching keyword data: {str(e)}")
            raise
    
    def _extract_keyword_texts(self, keywords_data: List[Any]) -> List[str]:
        """
        从关键词数据中提取文本
        
        Args:
            keywords_data: 关键词数据列表
        
        Returns:
            关键词文本列表
        """
        keywords = []
        for item in keywords_data:
            if isinstance(item, str):
                keywords.append(item)
            elif isinstance(item, dict):
                # 尝试多个可能的字段名
                keyword = item.get('keyword') or item.get('Keyword') or item.get('word')
                if keyword:
                    keywords.append(str(keyword))
        
        # 去重并保持顺序
        seen = set()
        unique_keywords = []
        for kw in keywords:
            kw_lower = kw.lower()
            if kw_lower not in seen:
                seen.add(kw_lower)
                unique_keywords.append(kw)
        
        return unique_keywords
    
    def _extract_keywords_from_title(self, title: str) -> List[str]:
        """
        从标题中提取关键词
        
        Args:
            title: 产品标题
        
        Returns:
            关键词列表
        """
        # 简单的分词逻辑
        import re
        
        # 移除特殊字符，保留字母、数字和空格
        cleaned = re.sub(r'[^\w\s]', ' ', title)
        
        # 分词
        words = cleaned.split()
        
        # 过滤停用词和短词
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with'}
        keywords = [w for w in words if len(w) > 2 and w.lower() not in stop_words]
        
        return keywords[:15]
    
    def _generate_long_tail_keywords(self, core_keywords: List[str]) -> List[str]:
        """
        生成长尾关键词
        
        基于核心关键词生成常见的长尾组合。
        
        Args:
            core_keywords: 核心关键词列表
        
        Returns:
            长尾关键词列表
        """
        if not core_keywords:
            return []
        
        long_tail = []
        modifiers = ['best', 'top', 'cheap', 'premium', 'professional', 'portable']
        
        # 生成一些简单的组合
        for kw in core_keywords[:5]:
            for modifier in modifiers[:3]:
                long_tail.append(f"{modifier} {kw}")
        
        return long_tail[:15]
    
    def _build_optimization_prompt(
        self,
        keyword_data: Dict[str, Any],
        include_bullet_points: bool
    ) -> str:
        """
        构建关键词优化 Prompt
        
        Args:
            keyword_data: 关键词数据
            include_bullet_points: 是否包含五点优化
        
        Returns:
            格式化的 Prompt
        """
        return self.prompts.keyword_optimization(
            asin=keyword_data.get("asin", ""),
            current_title=keyword_data.get("current_title", ""),
            category=keyword_data.get("category", ""),
            core_keywords=keyword_data.get("core_keywords", []),
            competitor_keywords=keyword_data.get("competitor_keywords", []),
            long_tail_keywords=keyword_data.get("long_tail_keywords", []),
            current_bullet_points=keyword_data.get("current_bullet_points", [])
        )
    
    def _extract_optimized_title(self, optimization_report: str) -> str:
        """
        从优化报告中提取优化后的标题
        
        Args:
            optimization_report: AI 生成的优化报告
        
        Returns:
            优化后的标题
        """
        import re
        
        # 尝试匹配 "## 优化后标题" 后面的内容
        patterns = [
            r'##\s*优化后标题\s*\n+(.+?)(?:\n\n|\*\*|##|$)',
            r'优化后的?标题[：:]\s*(.+?)(?:\n\n|\*\*|##|$)',
            r'新标题[：:]\s*(.+?)(?:\n\n|\*\*|##|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, optimization_report, re.DOTALL)
            if match:
                title = match.group(1).strip()
                # 移除可能的 markdown 格式
                title = re.sub(r'\*\*|__', '', title)
                # 只取第一行
                title = title.split('\n')[0].strip()
                if title and len(title) > 20:  # 确保标题有意义
                    return title
        
        # 如果无法提取，返回提示信息
        logger.warning("Could not extract optimized title from report")
        return "优化标题提取失败，请查看完整报告"
    
    def generate_cache_key(self, asin: str, domain: int) -> str:
        """
        生成缓存键
        
        Args:
            asin: 产品 ASIN
            domain: 站点代码
        
        Returns:
            缓存键（MD5 哈希）
        """
        key_data = {
            "type": "keyword_optimization",
            "asin": asin,
            "domain": domain
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
