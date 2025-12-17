# API 调用成本优化方案

**文档编号**: 007-COST-OPT  
**创建日期**: 2025-12-17  
**优先级**: 高  
**预估节省**: 70-80% 成本

---

## 📊 当前成本分析

### API 调用情况

| API 类型 | 单次成本 | 月度调用量 | 月度成本 | 占比 |
|---------|---------|-----------|---------|------|
| **DeepSeek AI** | $0.003 | 1,000 | $3.00 | 15% |
| **Sorftime API** | $0.02 | 1,000 | $20.00 | 85% |
| **总计** | - | 2,000 | **$23.00** | 100% |

### 成本构成分析

1. **Sorftime API** (85%)
   - 每次选品分析：3-4 次调用
   - 每次关键词优化：2-3 次调用
   - 平均单次成本：$0.02

2. **DeepSeek AI** (15%)
   - 平均 Token 消耗：3,000 tokens
   - 单次成本：~$0.003
   - 可优化空间大

---

## 🎯 优化目标

### 短期目标（1 个月）
- 降低 50% API 调用次数
- 节省 $11.50/月

### 中期目标（3 个月）
- 降低 70% API 调用次数
- 节省 $16.10/月

### 长期目标（6 个月）
- 降低 80% API 调用次数
- 节省 $18.40/月
- 建立完善的缓存体系

---

## 💡 优化方案

### 方案 1: 多级缓存策略 ⭐⭐⭐⭐⭐

**优先级**: P0（最高）  
**预估节省**: 60-70%  
**实施难度**: 中等  
**实施时间**: 3-5 天

#### 1.1 Redis 缓存层

**目标**: 缓存 API 响应，避免重复调用

**实施方案**:

```python
# backend/app/services/cache_service.py

import redis
import json
import hashlib
from typing import Optional, Any
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class CacheService:
    """多级缓存服务"""
    
    def __init__(self, redis_url: str):
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.default_ttl = 86400  # 24 小时
    
    async def get(self, key: str) -> Optional[dict]:
        """获取缓存"""
        try:
            data = self.redis_client.get(key)
            if data:
                logger.info(f"Cache hit: {key}")
                return json.loads(data)
            logger.info(f"Cache miss: {key}")
            return None
        except Exception as e:
            logger.error(f"Cache get error: {str(e)}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: dict, 
        ttl: int = None
    ) -> bool:
        """设置缓存"""
        try:
            ttl = ttl or self.default_ttl
            self.redis_client.setex(
                key, 
                ttl, 
                json.dumps(value)
            )
            logger.info(f"Cache set: {key}, TTL: {ttl}s")
            return True
        except Exception as e:
            logger.error(f"Cache set error: {str(e)}")
            return False
    
    def generate_key(self, prefix: str, **params) -> str:
        """生成缓存键"""
        # 排序参数确保一致性
        sorted_params = sorted(params.items())
        param_str = json.dumps(sorted_params)
        hash_str = hashlib.md5(param_str.encode()).hexdigest()
        return f"{prefix}:{hash_str}"
```

**缓存策略**:

| 数据类型 | TTL | 原因 |
|---------|-----|------|
| 选品分析 | 24 小时 | 市场数据变化慢 |
| 关键词优化 | 12 小时 | 关键词相对稳定 |
| 产品详情 | 6 小时 | 价格可能变化 |
| 类目数据 | 48 小时 | 类目结构稳定 |

**预期效果**:
- 缓存命中率：70-80%
- 成本节省：60-70%
- 响应速度提升：10-50 倍

---

#### 1.2 数据库缓存层

**目标**: 持久化历史分析结果

**实施方案**:

```python
# 在 ProductSelectionService 中集成缓存

class ProductSelectionService:
    def __init__(
        self,
        sorftime_client: SorftimeClient,
        deepseek_client: DeepSeekClient,
        cache_service: CacheService,
        db_session: Session
    ):
        self.sorftime = sorftime_client
        self.ai = deepseek_client
        self.cache = cache_service
        self.db = db_session
    
    async def analyze_category(
        self,
        category_id: str,
        domain: int = 1,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        # 1. 检查 Redis 缓存
        if use_cache:
            cache_key = self.cache.generate_key(
                "product_selection",
                category_id=category_id,
                domain=domain
            )
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return cached_result
        
        # 2. 检查数据库缓存（7 天内）
        if use_cache:
            db_result = self.db.query(ProductSelectionReport).filter(
                ProductSelectionReport.category_id == category_id,
                ProductSelectionReport.domain == domain,
                ProductSelectionReport.created_at > datetime.utcnow() - timedelta(days=7)
            ).order_by(ProductSelectionReport.created_at.desc()).first()
            
            if db_result:
                result = {
                    "category_id": db_result.category_id,
                    "category_name": db_result.category_name,
                    "market_score": db_result.market_score,
                    "analysis": db_result.analysis,
                    # ...
                }
                # 回写到 Redis
                await self.cache.set(cache_key, result, ttl=86400)
                return result
        
        # 3. 调用 API 获取新数据
        result = await self._fetch_and_analyze(category_id, domain)
        
        # 4. 保存到数据库
        report = ProductSelectionReport(**result)
        self.db.add(report)
        self.db.commit()
        
        # 5. 保存到 Redis
        if use_cache:
            await self.cache.set(cache_key, result, ttl=86400)
        
        return result
```

**预期效果**:
- 历史数据复用率：30-40%
- 额外成本节省：10-15%

---

### 方案 2: Prompt 优化 ⭐⭐⭐⭐⭐

**优先级**: P0（最高）  
**预估节省**: 30-40% AI 成本  
**实施难度**: 低  
**实施时间**: 1-2 天

#### 2.1 精简 Prompt

**当前问题**:
- Prompt 过长，包含大量示例
- Token 消耗：3,000-4,000 tokens
- 单次成本：$0.003-0.004

**优化方案**:

```python
# 优化前
def product_selection_analysis(self, ...):
    prompt = f"""你是一位资深的亚马逊选品专家，拥有 10 年以上的跨境电商经验。
    
请基于以下数据分析该类目的选品机会。

## 类目信息
- 类目名称: {category_name}
- 月销量趋势: {sales_trend}
...（大量详细说明）

## 分析要求
请从以下角度进行深度分析：
1. 市场容量和增长潜力
   - 评估市场规模和增长趋势
   - 识别市场机会和空白点
   ...（详细要求）

## 输出格式
请严格按照以下 Markdown 格式输出：
```markdown
## 市场机会评分：X/10
...（详细格式说明）
```

"""

# 优化后（减少 40% Token）
def product_selection_analysis_optimized(self, ...):
    prompt = f"""作为亚马逊选品专家，分析以下类目：

类目：{category_name}
销量趋势：{sales_trend}
Top 10 产品：{products_summary}  # 精简版
均价：${avg_price}，评分：{avg_rating}星

输出（Markdown）：
## 评分：X/10
### 市场分析
[市场容量、增长、竞争]
### 选品建议（3个）
1. **产品类型** (X/10) - 缺口/价格/月销
### 风险
- [3个风险点]
"""

```

**优化要点**:
1. 移除冗余说明
2. 精简产品列表（只保留关键字段）
3. 简化输出格式要求
4. 使用缩写和简洁表达

**预期效果**:
- Token 减少：40%
- 成本节省：$0.001/次
- 月度节省：$1.00（1000 次）

---

#### 2.2 智能 Prompt 模板

**方案**: 根据场景使用不同复杂度的 Prompt

```python
class PromptTemplates:
    @staticmethod
    def product_selection_analysis(
        category_data: dict,
        mode: str = "standard"  # simple, standard, detailed
    ) -> str:
        if mode == "simple":
            # 快速分析，Token 少
            return PromptTemplates._simple_analysis(category_data)
        elif mode == "detailed":
            # 深度分析，Token 多
            return PromptTemplates._detailed_analysis(category_data)
        else:
            # 标准分析
            return PromptTemplates._standard_analysis(category_data)
```

---

### 方案 3: 批量处理 ⭐⭐⭐⭐

**优先级**: P1  
**预估节省**: 20-30%  
**实施难度**: 中等  
**实施时间**: 2-3 天

#### 3.1 批量 API 调用

**方案**: 合并多个请求为一次调用

```python
# 优化前：单个调用
for asin in asins:
    result = await sorftime.product_request(asin=asin, domain=1)
    # 10 个 ASIN = 10 次调用

# 优化后：批量调用
asins_str = ','.join(asins)  # 最多 10 个
result = await sorftime.product_request(asin=asins_str, domain=1)
# 10 个 ASIN = 1 次调用
```

**预期效果**:
- API 调用减少：80-90%
- 成本节省：$0.18/10 个产品

---

#### 3.2 AI 批量分析

**方案**: 一次 AI 调用分析多个产品

```python
# 优化前
for product in products:
    analysis = await ai.analyze(product)  # 10 次 AI 调用

# 优化后
batch_prompt = f"""分析以下 10 个产品：
1. {product1_summary}
2. {product2_summary}
...
输出：每个产品一行评分和建议
"""
batch_analysis = await ai.analyze(batch_prompt)  # 1 次 AI 调用
```

**预期效果**:
- AI 调用减少：90%
- 成本节省：$0.027/10 个产品

---

### 方案 4: 智能降级策略 ⭐⭐⭐

**优先级**: P1  
**预估节省**: 15-20%  
**实施难度**: 低  
**实施时间**: 1 天

#### 4.1 数据降级

**方案**: 根据需求使用不同精度的数据

```python
class ProductSelectionService:
    async def analyze_category(
        self,
        category_id: str,
        domain: int = 1,
        detail_level: str = "standard"  # basic, standard, full
    ):
        if detail_level == "basic":
            # 只获取 Best Sellers，不获取趋势和详情
            bestsellers = await self.sorftime.category_request(...)
            # 节省 2 次 API 调用
        elif detail_level == "full":
            # 获取完整数据
            bestsellers = await self.sorftime.category_request(...)
            trend = await self.sorftime.category_trend(...)
            products = await self.sorftime.product_request(...)
        else:
            # 标准模式
            bestsellers = await self.sorftime.category_request(...)
            products = await self.sorftime.product_request(...)
```

---

#### 4.2 AI 模型降级

**方案**: 简单任务使用便宜模型

```python
class DeepSeekClient:
    async def chat_completion(
        self,
        messages: List[Dict],
        task_complexity: str = "standard"  # simple, standard, complex
    ):
        if task_complexity == "simple":
            model = "deepseek-chat-lite"  # 便宜 50%
        else:
            model = "deepseek-chat"
        
        # 调用 API
        ...
```

**预期效果**:
- 简单任务成本减半
- 整体节省：15-20%

---

### 方案 5: 请求去重和合并 ⭐⭐⭐⭐

**优先级**: P1  
**预估节省**: 10-15%  
**实施难度**: 低  
**实施时间**: 1 天

#### 5.1 请求去重

**方案**: 短时间内相同请求只执行一次

```python
from asyncio import Lock
from typing import Dict, Any

class RequestDeduplicator:
    """请求去重器"""
    
    def __init__(self):
        self.pending_requests: Dict[str, Any] = {}
        self.locks: Dict[str, Lock] = {}
    
    async def execute(self, key: str, func, *args, **kwargs):
        """执行去重请求"""
        # 如果已有相同请求在处理中，等待结果
        if key in self.pending_requests:
            logger.info(f"Request deduplication: {key}")
            return await self.pending_requests[key]
        
        # 创建锁
        if key not in self.locks:
            self.locks[key] = Lock()
        
        async with self.locks[key]:
            # 双重检查
            if key in self.pending_requests:
                return await self.pending_requests[key]
            
            # 执行请求
            task = asyncio.create_task(func(*args, **kwargs))
            self.pending_requests[key] = task
            
            try:
                result = await task
                return result
            finally:
                # 清理
                del self.pending_requests[key]
```

**预期效果**:
- 并发重复请求减少：100%
- 成本节省：10-15%

---

### 方案 6: 数据预热和预加载 ⭐⭐⭐

**优先级**: P2  
**预估节省**: 5-10%  
**实施难度**: 中等  
**实施时间**: 2 天

#### 6.1 热门数据预热

**方案**: 定时预加载热门类目数据

```python
# backend/app/tasks/cache_warmup.py

from celery import Celery
from app.services.ai import ProductSelectionService

celery_app = Celery('tasks')

@celery_app.task
def warmup_popular_categories():
    """预热热门类目"""
    popular_categories = [
        "172282",  # Electronics
        "2619525011",  # Home & Kitchen
        # ... 其他热门类目
    ]
    
    service = ProductSelectionService(...)
    
    for category_id in popular_categories:
        # 预加载数据到缓存
        await service.analyze_category(
            category_id=category_id,
            domain=1,
            use_cache=True
        )

# 每天凌晨 2 点执行
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=2, minute=0),
        warmup_popular_categories.s(),
    )
```

**预期效果**:
- 热门类目命中率：90%+
- 用户体验提升
- 成本节省：5-10%

---

## 📊 综合优化效果

### 成本对比

| 方案 | 节省比例 | 月度节省 | 实施难度 | 优先级 |
|------|---------|---------|---------|--------|
| 多级缓存 | 60-70% | $13.80-16.10 | 中等 | P0 |
| Prompt 优化 | 30-40% | $0.90-1.20 | 低 | P0 |
| 批量处理 | 20-30% | $4.60-6.90 | 中等 | P1 |
| 智能降级 | 15-20% | $3.45-4.60 | 低 | P1 |
| 请求去重 | 10-15% | $2.30-3.45 | 低 | P1 |
| 数据预热 | 5-10% | $1.15-2.30 | 中等 | P2 |

### 组合效果（非简单叠加）

**实施 P0 方案**:
- 预估节省：70%
- 月度成本：$23.00 → $6.90
- 节省：$16.10/月

**实施 P0 + P1 方案**:
- 预估节省：80%
- 月度成本：$23.00 → $4.60
- 节省：$18.40/月

**实施全部方案**:
- 预估节省：85%
- 月度成本：$23.00 → $3.45
- 节省：$19.55/月

---

## 🚀 实施计划

### 第 1 周：P0 方案

**Day 1-2**: Redis 缓存层
- 安装 Redis
- 实现 CacheService
- 集成到选品服务

**Day 3**: 数据库缓存层
- 修改服务逻辑
- 添加数据库查询

**Day 4-5**: Prompt 优化
- 精简 Prompt 模板
- 实现多级 Prompt
- 测试效果

### 第 2 周：P1 方案

**Day 6-7**: 批量处理
- 实现批量 API 调用
- 实现批量 AI 分析

**Day 8**: 智能降级
- 实现数据降级
- 实现模型降级

**Day 9**: 请求去重
- 实现去重器
- 集成到服务

**Day 10**: 测试和优化
- 性能测试
- 成本统计
- 优化调整

---

## 📈 监控和度量

### 关键指标

```python
# backend/app/services/metrics_service.py

class MetricsService:
    """成本监控服务"""
    
    def track_api_call(
        self,
        api_type: str,  # sorftime, deepseek
        endpoint: str,
        cost: float,
        cached: bool
    ):
        """记录 API 调用"""
        # 保存到数据库
        # 实时统计
        pass
    
    def get_daily_cost(self, date: datetime) -> dict:
        """获取每日成本"""
        return {
            "total_calls": 100,
            "cached_calls": 70,
            "cache_hit_rate": 0.7,
            "total_cost": 0.30,
            "saved_cost": 0.70
        }
```

### 监控面板

```
┌─────────────────────────────────────────┐
│  成本监控面板                            │
├─────────────────────────────────────────┤
│  今日统计:                               │
│  - 总调用: 100 次                        │
│  - 缓存命中: 70 次 (70%)                 │
│  - 实际调用: 30 次                       │
│  - 总成本: $0.30                         │
│  - 节省成本: $0.70 (70%)                 │
├─────────────────────────────────────────┤
│  本月统计:                               │
│  - 总成本: $6.90                         │
│  - 预算: $23.00                          │
│  - 节省: $16.10 (70%)                    │
└─────────────────────────────────────────┘
```

---

## ✅ 成功标准

1. **缓存命中率** > 70%
2. **API 调用减少** > 60%
3. **成本节省** > 70%
4. **响应速度** 提升 10 倍+
5. **用户体验** 无明显下降

---

## 🎯 总结

### 立即实施（本周）
1. ✅ Redis 缓存层
2. ✅ Prompt 优化
3. ✅ 数据库缓存

**预期效果**: 节省 70% 成本

### 后续优化（下周）
4. ✅ 批量处理
5. ✅ 智能降级
6. ✅ 请求去重

**预期效果**: 额外节省 10-15% 成本

### 长期优化（下月）
7. ✅ 数据预热
8. ✅ 成本监控
9. ✅ 持续优化

**预期效果**: 总节省 85% 成本

---

**文档版本**: 1.0  
**最后更新**: 2025-12-17  
**作者**: AI Assistant  
**状态**: 待实施
