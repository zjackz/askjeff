"""
AI Prompt 模板系统

提供结构化的 Prompt 模板，用于生成高质量的 AI 分析结果。
"""

from typing import List, Dict, Any, Optional


class PromptTemplates:
    """AI Prompt 模板库"""
    
    @staticmethod
    def product_selection_analysis(
        category_name: str,
        sales_trend: str,
        top_products: List[Dict[str, Any]],
        avg_price: float,
        avg_rating: float,
        avg_reviews: int = 0,
        competition_level: str = "中等"
    ) -> str:
        """
        选品分析 Prompt
        
        Args:
            category_name: 类目名称
            sales_trend: 销量趋势描述
            top_products: Top 10 产品列表
            avg_price: 平均价格
            avg_rating: 平均评分
            avg_reviews: 平均评论数
            competition_level: 竞争强度
        
        Returns:
            格式化的 Prompt 字符串
        """
        # 格式化产品列表
        products_text = PromptTemplates._format_products(top_products)
        
        prompt = f"""你是一位资深的亚马逊选品专家，拥有 10 年以上的跨境电商经验。请基于以下数据分析该类目的选品机会。

## 类目信息

- **类目名称**: {category_name}
- **月销量趋势**: {sales_trend}
- **平均价格**: ${avg_price:.2f}
- **平均评分**: {avg_rating:.1f} 星
- **平均评论数**: {avg_reviews} 条
- **竞争强度**: {competition_level}

## Top 10 产品数据

{products_text}

## 分析要求

请从以下角度进行深度分析：

1. **市场容量和增长潜力**
   - 评估市场规模和增长趋势
   - 识别市场机会和空白点
   - 预测未来 6-12 个月发展

2. **竞争强度评估**
   - 分析竞争格局（低/中/高）
   - 识别主要竞争对手特征
   - 评估新卖家进入难度

3. **价格区间建议**
   - 推荐最优价格区间
   - 分析价格与销量的关系
   - 考虑利润空间

4. **产品差异化方向**
   - 提供至少 3 个具体的差异化建议
   - 基于市场缺口和用户需求
   - 考虑可实现性

5. **风险提示**
   - 识别主要风险点
   - 提供风险规避建议

## 输出格式

请严格按照以下 Markdown 格式输出：

```markdown
## 市场机会评分：X/10

### 市场分析

[详细的市场分析，包括市场容量、增长潜力、竞争格局等]

### 选品建议

#### 1. [产品类型名称] (推荐指数: X/10)

- **市场缺口**: [说明市场上缺少什么]
- **建议价格**: $XX-XX
- **差异化点**: [具体的差异化方向]
- **预估月销**: XXX-XXX 单
- **利润空间**: XX-XX%

#### 2. [产品类型名称] (推荐指数: X/10)

[同上格式]

#### 3. [产品类型名称] (推荐指数: X/10)

[同上格式]

### 风险提示

- ⚠️ [风险点 1]
- ⚠️ [风险点 2]
- ⚠️ [风险点 3]

### 行动建议

1. [具体的下一步行动]
2. [具体的下一步行动]
3. [具体的下一步行动]
```

**注意事项**:
- 评分要客观，基于数据
- 建议要具体可执行
- 避免过于乐观或悲观
- 考虑实际运营难度
"""
        return prompt
    
    @staticmethod
    def keyword_optimization(
        asin: str,
        current_title: str,
        category: str,
        core_keywords: List[str],
        competitor_keywords: List[str],
        long_tail_keywords: Optional[List[str]] = None,
        current_bullet_points: Optional[List[str]] = None
    ) -> str:
        """
        关键词优化 Prompt
        
        Args:
            asin: 产品 ASIN
            current_title: 当前标题
            category: 产品类目
            core_keywords: 核心关键词列表
            competitor_keywords: 竞品高频关键词
            long_tail_keywords: 长尾关键词（可选）
            current_bullet_points: 当前五点描述（可选）
        
        Returns:
            格式化的 Prompt 字符串
        """
        # 格式化关键词列表
        core_kw_text = ', '.join(core_keywords[:15])
        comp_kw_text = ', '.join(competitor_keywords[:15])
        long_tail_text = ', '.join(long_tail_keywords[:10]) if long_tail_keywords else "暂无"
        
        # 格式化当前五点
        bullet_points_text = ""
        if current_bullet_points:
            bullet_points_text = "\n".join([f"{i+1}. {bp}" for i, bp in enumerate(current_bullet_points)])
        else:
            bullet_points_text = "暂无"
        
        prompt = f"""你是一位专业的亚马逊 Listing 优化专家，精通 SEO 和转化率优化。请优化以下产品的关键词和 Listing。

## 产品信息

- **ASIN**: {asin}
- **类目**: {category}
- **当前标题**: {current_title}

## 当前五点描述

{bullet_points_text}

## 关键词数据

### 核心关键词（高搜索量）
{core_kw_text}

### 竞品高频关键词
{comp_kw_text}

### 长尾关键词
{long_tail_text}

## 优化要求

请提供以下优化建议：

1. **优化后的标题**
   - 长度：180-200 字符
   - 包含核心关键词，但不堆砌
   - 自然流畅，符合英文表达习惯
   - 突出产品核心卖点
   - 遵守 Amazon 标题规范（不含促销语、特殊符号等）

2. **优化后的五点描述**
   - 每点 200-250 字符
   - 每点突出一个核心卖点
   - 自然融入关键词
   - 使用 AIDA 模型（注意力、兴趣、欲望、行动）
   - 解决客户痛点

3. **后台搜索词建议**
   - 总长度不超过 250 字节
   - 包含长尾词和同义词
   - 避免重复标题中的词
   - 用空格分隔，不用逗号

4. **关键词策略说明**
   - 解释关键词选择逻辑
   - 说明优化思路
   - 提供 A/B 测试建议

## 输出格式

请严格按照以下 Markdown 格式输出：

```markdown
## 优化后标题

[新标题内容]

**字符数**: XXX

## 优化后五点描述

### Bullet Point 1
[内容]

### Bullet Point 2
[内容]

### Bullet Point 3
[内容]

### Bullet Point 4
[内容]

### Bullet Point 5
[内容]

## 后台搜索词

[关键词列表，空格分隔]

**字节数**: XXX/250

## 优化说明

### 标题优化思路
[详细说明标题优化的考虑因素]

### 五点优化思路
[详细说明五点描述的优化策略]

### 关键词策略
- **核心词布局**: [说明]
- **长尾词应用**: [说明]
- **竞品词借鉴**: [说明]

### A/B 测试建议
1. [测试建议 1]
2. [测试建议 2]

### 预期效果
- 搜索曝光提升: XX-XX%
- 点击率提升: XX-XX%
- 转化率提升: XX-XX%
```

**注意事项**:
- 确保所有内容符合 Amazon 政策
- 避免夸大宣传和虚假承诺
- 关键词使用要自然，不堆砌
- 考虑移动端显示效果
"""
        return prompt
    
    @staticmethod
    def competitor_analysis(
        my_asin: str,
        competitor_asins: List[str],
        my_product_data: Dict[str, Any],
        competitor_products_data: List[Dict[str, Any]]
    ) -> str:
        """
        竞品分析 Prompt
        
        Args:
            my_asin: 我的产品 ASIN
            competitor_asins: 竞品 ASIN 列表
            my_product_data: 我的产品数据
            competitor_products_data: 竞品数据列表
        
        Returns:
            格式化的 Prompt 字符串
        """
        # 格式化我的产品信息
        my_info = f"""
- **ASIN**: {my_asin}
- **标题**: {my_product_data.get('title', 'N/A')}
- **价格**: ${my_product_data.get('price', 0):.2f}
- **评分**: {my_product_data.get('ratings', 0):.1f} 星
- **评论数**: {my_product_data.get('ratingsCount', 0)} 条
- **月销量**: {my_product_data.get('listingSalesVolumeOfMonth', 0)} 单
"""
        
        # 格式化竞品信息
        comp_info = []
        for i, comp in enumerate(competitor_products_data[:5], 1):
            comp_info.append(f"""
#### 竞品 {i}
- **ASIN**: {comp.get('asin', 'N/A')}
- **标题**: {comp.get('title', 'N/A')}
- **价格**: ${comp.get('price', 0):.2f}
- **评分**: {comp.get('ratings', 0):.1f} 星
- **评论数**: {comp.get('ratingsCount', 0)} 条
- **月销量**: {comp.get('listingSalesVolumeOfMonth', 0)} 单
""")
        
        comp_text = '\n'.join(comp_info)
        
        prompt = f"""你是一位资深的亚马逊运营专家。请对比分析我的产品和竞品，提供改进建议。

## 我的产品

{my_info}

## 主要竞品

{comp_text}

## 分析要求

请从以下维度进行对比分析：

1. **价格策略对比**
2. **产品质量对比**（基于评分和评论）
3. **销量表现对比**
4. **Listing 优化程度对比**
5. **差异化优势和劣势**

## 输出格式

```markdown
## 竞品对比分析

### 价格定位
[分析我的产品价格是否合理，相比竞品的优劣势]

### 市场表现
[对比销量、评分、评论数，分析差距原因]

### 优势分析
1. [我的产品优势 1]
2. [我的产品优势 2]
3. [我的产品优势 3]

### 劣势分析
1. [我的产品劣势 1]
2. [我的产品劣势 2]
3. [我的产品劣势 3]

### 改进建议
1. [具体改进建议 1]
2. [具体改进建议 2]
3. [具体改进建议 3]

### 竞争策略
[提供具体的竞争策略建议]
```
"""
        return prompt
    
    @staticmethod
    def _format_products(products: List[Dict[str, Any]]) -> str:
        """
        格式化产品列表为文本
        
        Args:
            products: 产品数据列表
        
        Returns:
            格式化的产品列表文本
        """
        if not products:
            return "暂无产品数据"
        
        formatted = []
        for i, product in enumerate(products[:10], 1):
            title = product.get('title', 'N/A')
            # 截断过长的标题
            if len(title) > 80:
                title = title[:77] + '...'
            
            price = product.get('price', 0)
            rating = product.get('ratings', 0)
            reviews = product.get('ratingsCount', 0)
            sales = product.get('listingSalesVolumeOfMonth', 0)
            
            formatted.append(f"""
### {i}. {title}
- **价格**: ${price:.2f}
- **评分**: {rating:.1f} 星
- **评论数**: {reviews} 条
- **月销量**: {sales} 单
""")
        
        return '\n'.join(formatted)
    
    @staticmethod
    def validate_prompt_length(prompt: str, max_tokens: int = 3000) -> bool:
        """
        验证 Prompt 长度是否合理
        
        Args:
            prompt: Prompt 文本
            max_tokens: 最大 token 数
        
        Returns:
            是否在合理范围内
        """
        # 粗略估算 token 数
        chinese_chars = sum(1 for c in prompt if '\u4e00' <= c <= '\u9fff')
        english_words = len(prompt.split())
        estimated_tokens = int(chinese_chars * 1.5 + english_words * 1.3)
        
        return estimated_tokens <= max_tokens
    
    @staticmethod
    def get_system_prompt(role: str = "amazon_expert") -> str:
        """
        获取系统提示词
        
        Args:
            role: 角色类型
        
        Returns:
            系统提示词
        """
        prompts = {
            "amazon_expert": "你是一位资深的亚马逊运营专家，拥有 10 年以上的跨境电商经验。你精通选品、关键词优化、Listing 优化、广告投放等各个环节。你的建议总是基于数据分析，具体可执行，并且考虑实际运营难度。",
            
            "seo_specialist": "你是一位专业的亚马逊 SEO 专家，精通关键词研究、Listing 优化和搜索排名提升。你了解 Amazon A9 算法的工作原理，能够提供有效的优化建议。",
            
            "data_analyst": "你是一位数据分析专家，擅长从海量数据中提取有价值的洞察。你能够识别市场趋势、发现商业机会，并提供数据驱动的决策建议。",
            
            "product_manager": "你是一位经验丰富的产品经理，擅长产品规划、市场定位和竞品分析。你能够从用户需求出发，提供产品差异化建议。"
        }
        
        return prompts.get(role, prompts["amazon_expert"])
