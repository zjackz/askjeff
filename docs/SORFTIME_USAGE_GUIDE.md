# Sorftime API 集成使用指南

## 📚 目录

1. [快速开始](#快速开始)
2. [API 概览](#api-概览)
3. [常用场景](#常用场景)
4. [最佳实践](#最佳实践)
5. [故障排查](#故障排查)

---

## 🚀 快速开始

### 前端测试控制台

访问 `/admin/sorftime-test` 页面，可以直接在浏览器中测试所有 45 个 Sorftime API。

**基本使用流程**：
1. 选择 API 端点
2. 填写必需参数
3. 点击"发送请求"
4. 查看响应数据（支持可视化和 JSON 视图）

### 后端集成示例

```python
from app.services.sorftime import SorftimeClient
import os

# 初始化客户端
client = SorftimeClient(account_sk=os.getenv("SORFTIME_API_KEY"))

# 查询产品信息
async def get_product_info(asin: str):
    response = await client.product_request(
        asin=asin,
        trend=1,  # 包含趋势数据
        domain=1  # 美国站
    )
    
    if response.code == 0:
        return response.data
    else:
        print(f"Error: {response.message}")
        return None

# 查询类目 Best Sellers
async def get_category_bestsellers(node_id: str):
    response = await client.category_request(
        node_id=node_id,
        domain=1
    )
    return response.data
```

---

## 📊 API 概览

### 基础查询 API (1-9)

| API | 端点 | 说明 | 消耗 |
|-----|------|------|------|
| 1 | ProductRequest | 产品详情查询 | 1-5 request |
| 2 | CategoryRequest | 类目 Best Sellers | 5 request |
| 3 | CategoryTree | 类目树结构 | 5 request |
| 4 | CategoryTrend | 类目趋势数据 | 5 request |
| 5 | CategoryProducts | 类目产品列表 | 5 request |
| 6 | ProductQuery | 产品搜索 | 5 request |
| 7 | KeywordQuery | 关键词搜索 | 5 request |
| 8 | KeywordRequest | 关键词详情 | 5 request |
| 9 | KeywordSearchResults | 关键词搜索结果 | 5 request |

### 高级数据 API (10-12)

| API | 端点 | 说明 | 消耗 |
|-----|------|------|------|
| 10 | AsinSalesVolume | ASIN 官方销量 | 1 request |
| 11 | ProductVariationHistory | 子体变化历史 | 1 request |
| 12 | ProductTrend | 产品趋势（设计中） | 1 request |

### 实时采集 API (13-20)

| API | 端点 | 说明 | 消耗 |
|-----|------|------|------|
| 13 | ProductRealtimeRequest | 实时产品数据 | 积分 |
| 14 | ProductRealtimeRequestStatusQuery | 查询实时任务状态 | 0 request |
| 15 | ProductReviewsCollection | 实时采集评论 | 积分 |
| 16 | ProductReviewsCollectionStatusQuery | 查询评论任务状态 | 0 request |
| 17 | ProductReviewsQuery | 查询已采集评论 | 0 request |
| 18 | SimilarProductRealtimeRequest | 图搜相似产品 | 积分 |
| 19 | SimilarProductRealtimeRequestStatusQuery | 查询图搜任务状态 | 0 request |
| 20 | SimilarProductRealtimeRequestCollection | 获取图搜结果 | 0 request |

### 关键词扩展 API (21-25)

| API | 端点 | 说明 | 消耗 |
|-----|------|------|------|
| 21 | KeywordSearchResultTrend | 搜索结果趋势 | 5 request |
| 22 | CategoryRequestKeyword | 类目反查关键词 | 5 request |
| 23 | ASINRequestKeyword | ASIN 反查关键词 | 5 request |
| 24 | KeywordProductRanking | 产品排名 | 2 request |
| 25 | ASINKeywordRanking | ASIN 排名趋势 | 2 request |

### 监控任务 API (26-42)

这些 API 用于创建和管理监控任务，消耗积分而非 request。包括：
- 关键词监控 (26-30)
- 榜单监控 (31-34)
- 跟卖&库存监控 (35-39)
- ASIN 订阅 (40-42)

### 账户/积分 API (43-45)

| API | 端点 | 说明 | 消耗 |
|-----|------|------|------|
| 43 | CoinQuery | 积分余额查询 | 1 request |
| 44 | CoinStream | 积分使用明细 | 1 request |
| 45 | RequestStream | Request 使用明细 | 1 request |

---

## 💡 常用场景

### 场景 1：竞品分析

```python
async def analyze_competitor(competitor_asin: str):
    """分析竞品的完整信息"""
    
    # 1. 获取产品详情
    product = await client.product_request(
        asin=competitor_asin,
        trend=1,
        domain=1
    )
    
    # 2. 反查关键词
    keywords = await client.asin_request_keyword(
        asin=competitor_asin,
        domain=1
    )
    
    # 3. 获取评论数据
    reviews = await client.product_reviews_query(
        asin=competitor_asin,
        query_start="2024-01-01",
        domain=1
    )
    
    return {
        "product": product.data,
        "keywords": keywords.data,
        "reviews": reviews.data
    }
```

### 场景 2：关键词研究

```python
async def research_keyword(keyword: str):
    """研究关键词的市场机会"""
    
    # 1. 获取关键词详情
    keyword_info = await client.keyword_request(
        keyword=keyword,
        domain=1
    )
    
    # 2. 获取搜索结果产品
    search_results = await client.keyword_search_results(
        keyword=keyword,
        page=1,
        domain=1
    )
    
    # 3. 获取产品排名
    rankings = await client.keyword_product_ranking(
        keyword=keyword,
        domain=1
    )
    
    return {
        "keyword_data": keyword_info.data,
        "top_products": search_results.data,
        "rankings": rankings.data
    }
```

### 场景 3：类目分析

```python
async def analyze_category(node_id: str):
    """分析类目的市场情况"""
    
    # 1. 获取类目 Best Sellers
    bestsellers = await client.category_request(
        node_id=node_id,
        domain=1
    )
    
    # 2. 获取类目趋势
    trend = await client.category_trend(
        node_id=node_id,
        trend_index=0,  # 销量趋势
        domain=1
    )
    
    # 3. 反查类目关键词
    keywords = await client.category_request_keyword(
        node_id=node_id,
        domain=1
    )
    
    return {
        "bestsellers": bestsellers.data,
        "trend": trend.data,
        "keywords": keywords.data
    }
```

---

## ✅ 最佳实践

### 1. 错误处理

```python
async def safe_api_call():
    try:
        response = await client.product_request(asin="B08N5WRWNW", domain=1)
        
        # 检查响应码
        if response.code == 0:
            return response.data
        elif response.code == 694:
            print("配额不足，请充值")
        elif response.code == 501:
            print("达到分钟限制，请稍后重试")
        else:
            print(f"API 错误: {response.message}")
            
    except Exception as e:
        print(f"请求失败: {str(e)}")
        return None
```

### 2. 批量查询优化

```python
async def batch_query_products(asins: list[str]):
    """批量查询产品（使用逗号分隔）"""
    
    # Sorftime 支持用逗号分隔多个 ASIN
    asin_str = ",".join(asins[:10])  # 最多 10 个
    
    response = await client.product_request(
        asin=asin_str,
        trend=0,  # 不包含趋势数据以节省时间
        domain=1
    )
    
    return response.data
```

### 3. 缓存策略

```python
from functools import lru_cache
import asyncio

# 简单的内存缓存
_cache = {}

async def get_category_tree_cached(domain: int = 1):
    """缓存类目树（数据量大且不常变化）"""
    cache_key = f"category_tree_{domain}"
    
    if cache_key in _cache:
        return _cache[cache_key]
    
    response = await client.category_tree(domain=domain)
    if response.code == 0:
        _cache[cache_key] = response.data
    
    return response.data
```

### 4. 速率限制处理

```python
import asyncio

async def rate_limited_requests(asins: list[str]):
    """遵守 API 速率限制（60次/分钟）"""
    results = []
    
    for i, asin in enumerate(asins):
        if i > 0 and i % 50 == 0:
            # 每 50 个请求暂停 60 秒
            await asyncio.sleep(60)
        
        response = await client.product_request(asin=asin, domain=1)
        results.append(response.data)
    
    return results
```

---

## 🔧 故障排查

### 常见错误码

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 0 | 成功 | - |
| 501 | 分钟限制 | 等待 60 秒后重试 |
| 694 | 配额不足 | 充值或等待下月 |
| 695 | 参数错误 | 检查请求参数格式 |
| 696 | 数据不存在 | 确认 ASIN/NodeId 正确 |

### 调试技巧

1. **启用详细日志**

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. **使用前端测试控制台**
   - 访问 `/admin/sorftime-test`
   - 可视化查看请求/响应
   - 复制生成的 payload

3. **检查 API Key**

```python
# 确保环境变量正确设置
import os
print(os.getenv("SORFTIME_API_KEY"))
```

4. **验证网络连接**

```bash
curl -X POST "https://standardapi.sorftime.com/api/ProductRequest?domain=1" \
  -H "Authorization: BasicAuth YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"ASIN":"B08N5WRWNW","Trend":1}'
```

---

## 📞 技术支持

- **文档**: `/docs/sorftimeAMAZON APIS.TXT`
- **测试控制台**: `/admin/sorftime-test`
- **类型定义**: `frontend/src/types/sorftime.ts`
- **后端客户端**: `backend/app/services/sorftime/client.py`

---

## 🔄 更新日志

### v1.0.0 (2024-12-17)
- ✅ 完整集成所有 45 个 API 端点
- ✅ 前端测试控制台
- ✅ 后端 Python 客户端
- ✅ TypeScript 类型定义
- ✅ 自动重试机制
- ✅ 详细日志记录
