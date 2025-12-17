# 成本优化实施指南：Redis 缓存集成

**文档编号**: 007-CACHE-IMPL  
**创建日期**: 2025-12-17  
**状态**: 实施中

---

## ✅ 已完成工作

### 1. CacheService 实现

**文件**: `backend/app/services/cache_service.py`

**功能**:
- ✅ 异步 Redis 操作
- ✅ 自动 JSON 序列化/反序列化
- ✅ TTL 管理（不同类型不同 TTL）
- ✅ 缓存键生成（MD5 哈希）
- ✅ 连接管理
- ✅ 统计信息

**代码量**: ~250 行

---

## 🔨 待集成工作

### 2. 集成到 ProductSelectionService

**修改文件**: `backend/app/services/ai/product_selection.py`

**需要修改的地方**:

```python
# 1. 添加导入
from app.services.cache_service import CacheService

# 2. 修改 __init__ 方法
class ProductSelectionService:
    def __init__(
        self,
        sorftime_client: SorftimeClient,
        deepseek_client: DeepSeekClient,
        cache_service: Optional[CacheService] = None  # 新增
    ):
        self.sorftime = sorftime_client
        self.ai = deepseek_client
        self.prompts = PromptTemplates()
        self.cache = cache_service  # 新增

# 3. 修改 analyze_category 方法
async def analyze_category(
    self,
    category_id: str,
    domain: int = 1,
    use_cache: bool = True
) -> Dict[str, Any]:
    logger.info(f"Starting category analysis: category_id={category_id}, domain={domain}")
    
    # 验证参数
    if not category_id:
        raise ValueError("category_id is required")
    
    # ===== 新增：检查缓存 =====
    if use_cache and self.cache:
        cache_key = self.cache.generate_key(
            "product_selection",
            category_id=category_id,
            domain=domain
        )
        cached_result = await self.cache.get(cache_key)
        if cached_result:
            logger.info(f"Returning cached result for {category_id}")
            return cached_result
    # ===== 缓存检查结束 =====
    
    # 1. 获取类目数据
    logger.info("Fetching category data from Sorftime API")
    category_data = await self._fetch_category_data(category_id, domain)
    
    # 2-4. 原有逻辑（构建 Prompt、AI 分析、解析结果）
    # ... 保持不变 ...
    
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
    
    # ===== 新增：保存到缓存 =====
    if use_cache and self.cache:
        ttl = self.cache.get_ttl_for_type("product_selection")  # 24 小时
        await self.cache.set(cache_key, result, ttl=ttl)
        logger.info(f"Cached result for {category_id}, TTL: {ttl}s")
    # ===== 缓存保存结束 =====
    
    logger.info(f"Analysis completed. Market score: {market_score}/10")
    return result
```

---

### 3. 集成到 KeywordOptimizationService

**修改文件**: `backend/app/services/ai/keyword_optimization.py`

**类似的修改**:
1. 添加 `cache_service` 参数
2. 在 `optimize_listing` 方法开头检查缓存
3. 在方法结尾保存到缓存

---

### 4. 更新 API 端点依赖注入

**修改文件**: `backend/app/api/v1/endpoints/ai.py`

```python
from app.services.cache_service import get_cache_service, CacheService

# 添加缓存服务依赖
def get_cache() -> CacheService:
    """获取缓存服务"""
    return get_cache_service()

# 更新服务依赖
def get_product_selection_service(
    sorftime: SorftimeClient = Depends(get_sorftime_client),
    deepseek: DeepSeekClient = Depends(get_deepseek_client),
    cache: CacheService = Depends(get_cache)  # 新增
) -> ProductSelectionService:
    """获取产品选品服务"""
    return ProductSelectionService(sorftime, deepseek, cache)  # 传入 cache

def get_keyword_optimization_service(
    sorftime: SorftimeClient = Depends(get_sorftime_client),
    deepseek: DeepSeekClient = Depends(get_deepseek_client),
    cache: CacheService = Depends(get_cache)  # 新增
) -> KeywordOptimizationService:
    """获取关键词优化服务"""
    return KeywordOptimizationService(sorftime, deepseek, cache)  # 传入 cache
```

---

### 5. 环境配置

**文件**: `.env`

```bash
# Redis 配置
REDIS_URL=redis://localhost:6379/0

# 或者使用 Docker
REDIS_URL=redis://redis:6379/0
```

**文件**: `docker-compose.yml`

```yaml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

volumes:
  redis_data:
```

---

### 6. 依赖安装

**文件**: `backend/requirements.txt`

```
redis[hiredis]>=5.0.0
```

**安装命令**:

```bash
cd backend
pip install redis[hiredis]
```

---

## 📊 预期效果

### 缓存命中率

| 场景 | 预期命中率 | 说明 |
|------|-----------|------|
| 热门类目 | 80-90% | 经常被查询 |
| 一般类目 | 60-70% | 偶尔被查询 |
| 冷门类目 | 20-30% | 很少被查询 |
| **平均** | **70%** | 总体预期 |

### 成本节省

**假设**:
- 每天 100 次查询
- 缓存命中率 70%
- 单次 API 成本 $0.023

**计算**:
- 无缓存成本：100 × $0.023 = $2.30/天
- 有缓存成本：30 × $0.023 = $0.69/天
- **节省**：$1.61/天 = **$48.30/月**

### 响应速度

| 场景 | 无缓存 | 有缓存 | 提升 |
|------|--------|--------|------|
| 选品分析 | 20-30s | 0.1-0.5s | **40-300 倍** |
| 关键词优化 | 15-20s | 0.1-0.5s | **30-200 倍** |

---

## 🧪 测试方案

### 1. 单元测试

```python
# tests/services/test_cache_service.py

import pytest
from app.services.cache_service import CacheService

@pytest.mark.asyncio
async def test_cache_set_and_get():
    cache = CacheService("redis://localhost:6379")
    await cache.connect()
    
    # 设置缓存
    key = "test_key"
    value = {"data": "test"}
    await cache.set(key, value, ttl=60)
    
    # 获取缓存
    result = await cache.get(key)
    assert result == value
    
    # 清理
    await cache.delete(key)
    await cache.disconnect()

@pytest.mark.asyncio
async def test_cache_miss():
    cache = CacheService("redis://localhost:6379")
    await cache.connect()
    
    result = await cache.get("nonexistent_key")
    assert result is None
    
    await cache.disconnect()
```

### 2. 集成测试

```python
# tests/api/test_ai_with_cache.py

@pytest.mark.asyncio
async def test_product_selection_with_cache(client):
    # 第一次调用（无缓存）
    response1 = client.post("/api/v1/ai/product-selection", json={
        "category_id": "172282",
        "domain": 1,
        "use_cache": True
    })
    assert response1.status_code == 200
    time1 = response1.elapsed.total_seconds()
    
    # 第二次调用（有缓存）
    response2 = client.post("/api/v1/ai/product-selection", json={
        "category_id": "172282",
        "domain": 1,
        "use_cache": True
    })
    assert response2.status_code == 200
    time2 = response2.elapsed.total_seconds()
    
    # 验证缓存效果
    assert time2 < time1 / 10  # 缓存应该快 10 倍以上
    assert response1.json()["market_score"] == response2.json()["market_score"]
```

---

## 📝 实施步骤

### Step 1: 启动 Redis（5 分钟）

```bash
# 使用 Docker
docker run -d --name redis -p 6379:6379 redis:7-alpine

# 或添加到 docker-compose.yml
docker-compose up -d redis
```

### Step 2: 安装依赖（2 分钟）

```bash
cd backend
pip install redis[hiredis]
```

### Step 3: 修改服务代码（30 分钟）

1. 修改 `ProductSelectionService.__init__`
2. 修改 `ProductSelectionService.analyze_category`
3. 修改 `KeywordOptimizationService.__init__`
4. 修改 `KeywordOptimizationService.optimize_listing`

### Step 4: 更新 API 端点（10 分钟）

1. 添加 `get_cache` 依赖
2. 更新服务依赖注入

### Step 5: 测试（15 分钟）

1. 启动服务
2. 测试选品 API（第一次慢，第二次快）
3. 测试关键词 API
4. 检查 Redis 数据

### Step 6: 监控（持续）

1. 观察缓存命中率
2. 统计成本节省
3. 优化 TTL 配置

---

## 🎯 成功标准

- ✅ Redis 服务正常运行
- ✅ 缓存命中率 > 70%
- ✅ 响应速度提升 > 10 倍
- ✅ 成本节省 > 60%
- ✅ 无功能回归问题

---

## 🚨 注意事项

1. **Redis 可用性**
   - 如果 Redis 不可用，服务应降级到无缓存模式
   - 已在 CacheService 中实现容错

2. **缓存失效**
   - 市场数据变化时需要手动清除缓存
   - 可以添加管理接口

3. **内存管理**
   - 监控 Redis 内存使用
   - 设置合理的 maxmemory 策略

4. **数据一致性**
   - 缓存的数据可能过时
   - 通过 TTL 控制新鲜度

---

## 📚 参考资料

- [Redis 官方文档](https://redis.io/docs/)
- [redis-py 文档](https://redis-py.readthedocs.io/)
- [FastAPI 依赖注入](https://fastapi.tiangolo.com/tutorial/dependencies/)

---

**文档版本**: 1.0  
**最后更新**: 2025-12-17  
**作者**: AI Assistant  
**状态**: CacheService 已实现，待集成到服务
