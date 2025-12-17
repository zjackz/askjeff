# 技术实施计划：AI 驱动的亚马逊运营提升方案 (MVP)

**需求编号**: 007  
**阶段**: MVP (阶段 1)  
**预估工时**: 2 周 (80 小时)  
**目标**: 实现核心功能，验证商业价值

---

## 🎯 MVP 范围

### 包含功能

1. **AI 智能选品助手** (基础版)
   - 类目市场分析
   - AI 生成选品报告
   - 简单的产品推荐

2. **AI 关键词优化引擎** (基础版)
   - ASIN 关键词反查
   - AI 生成优化建议
   - Listing 标题优化

### 不包含（后续阶段）

- 定价策略
- 竞品监控
- 评论分析
- 趋势预测
- 运营日报

---

## 🏗️ 技术架构

### 系统组件

```
┌─────────────────────────────────────────────────────────┐
│                    前端 (Vue 3)                          │
│  ┌──────────────────┐  ┌──────────────────┐            │
│  │  AI 选品助手页面 │  │ AI 关键词优化页面│            │
│  │  - 类目选择      │  │  - ASIN 输入     │            │
│  │  - 分析结果展示  │  │  - 优化建议展示  │            │
│  │  - Markdown 渲染 │  │  - 对比视图      │            │
│  └──────────────────┘  └──────────────────┘            │
└─────────────────────────────────────────────────────────┘
                          ↓ HTTP/REST
┌─────────────────────────────────────────────────────────┐
│                  后端 (FastAPI)                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │           AI 服务模块                             │  │
│  │  /api/v1/ai/product-selection                    │  │
│  │  /api/v1/ai/keyword-optimization                 │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │         业务逻辑层                                │  │
│  │  - ProductSelectionService                       │  │
│  │  - KeywordOptimizationService                    │  │
│  │  - PromptBuilder                                 │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │         数据访问层                                │  │
│  │  - SorftimeClient (已有)                         │  │
│  │  - DeepSeekClient (新建)                         │  │
│  │  - CacheService (Redis)                          │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 📂 目录结构

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   │           └── ai.py                    # 新增：AI 端点
│   ├── services/
│   │   ├── ai/
│   │   │   ├── __init__.py
│   │   │   ├── deepseek_client.py          # 新增：DeepSeek 客户端
│   │   │   ├── product_selection.py        # 新增：选品服务
│   │   │   ├── keyword_optimization.py     # 新增：关键词服务
│   │   │   └── prompts.py                  # 新增：Prompt 模板
│   │   └── sorftime/
│   │       └── client.py                   # 已有
│   ├── models/
│   │   └── ai.py                           # 新增：AI 相关模型
│   └── schemas/
│       └── ai.py                           # 新增：AI 请求/响应 Schema

frontend/
├── src/
│   ├── views/
│   │   └── ai/
│   │       ├── ProductSelection.vue        # 新增：选品页面
│   │       └── KeywordOptimization.vue     # 新增：关键词页面
│   ├── api/
│   │   └── ai.ts                           # 新增：AI API 客户端
│   └── types/
│       └── ai.ts                           # 新增：AI 类型定义
```

---

## 🔨 实施任务分解

### 第 1 天：环境准备和基础设施

#### 任务 1.1: DeepSeek API 集成 (4h)

**文件**: `backend/app/services/ai/deepseek_client.py`

```python
import httpx
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class DeepSeekClient:
    """DeepSeek API 客户端"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> str:
        """调用 DeepSeek Chat API"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                },
                timeout=60.0
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
```

#### 任务 1.2: Prompt 模板系统 (2h)

**文件**: `backend/app/services/ai/prompts.py`

```python
from typing import Dict, Any

class PromptTemplates:
    """AI Prompt 模板库"""
    
    @staticmethod
    def product_selection_analysis(
        category_name: str,
        sales_trend: str,
        top_products: List[Dict],
        avg_price: float,
        avg_rating: float
    ) -> str:
        """选品分析 Prompt"""
        return f"""你是一位资深的亚马逊选品专家。请基于以下数据分析该类目的选品机会。

类目信息：
- 类目名称：{category_name}
- 月销量趋势：{sales_trend}
- 平均价格：${avg_price}
- 平均评分：{avg_rating}

Top 10 产品：
{self._format_products(top_products)}

请从以下角度进行分析：
1. 市场容量和增长潜力
2. 竞争强度评估（低/中/高）
3. 价格区间建议
4. 产品差异化方向（至少 3 个）
5. 风险提示

输出格式（Markdown）：
## 市场机会评分：X/10

### 市场分析
[详细分析]

### 选品建议
1. **产品类型** (推荐指数: X/10)
   - 市场缺口：[说明]
   - 建议价格：$XX-XX
   - 差异化点：[说明]
   - 预估月销：XXX 单

### 风险提示
- [风险 1]
- [风险 2]
"""
    
    @staticmethod
    def keyword_optimization(
        asin: str,
        current_title: str,
        category: str,
        core_keywords: List[str],
        competitor_keywords: List[str]
    ) -> str:
        """关键词优化 Prompt"""
        return f"""你是一位专业的亚马逊 Listing 优化专家。请优化以下产品的关键词和标题。

产品信息：
- ASIN: {asin}
- 当前标题：{current_title}
- 类目：{category}

关键词数据：
- 核心关键词：{', '.join(core_keywords[:10])}
- 竞品高频词：{', '.join(competitor_keywords[:10])}

请提供：
1. 优化后的标题（200 字符内）
2. 优化建议说明
3. 关键词使用策略

要求：
- 标题自然流畅，符合英文表达习惯
- 包含核心关键词，但不堆砌
- 突出产品卖点和差异化
- 遵守 Amazon 标题规范

输出格式（Markdown）：
## 优化后标题
[新标题]

## 优化说明
[详细说明优化思路]

## 关键词策略
- 核心词：[列表]
- 长尾词：[列表]
- 使用建议：[说明]
"""
```

#### 任务 1.3: 数据库模型 (2h)

**文件**: `backend/app/models/ai.py`

```python
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text
from sqlalchemy.sql import func
from app.db.base_class import Base

class ProductSelectionReport(Base):
    """选品报告"""
    __tablename__ = "product_selection_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(String, index=True)
    category_name = Column(String)
    market_score = Column(Float)  # 1-10
    analysis = Column(Text)  # AI 生成的 Markdown 报告
    raw_data = Column(JSON)  # 原始数据
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, nullable=True)  # 可选：用户 ID

class KeywordOptimization(Base):
    """关键词优化记录"""
    __tablename__ = "keyword_optimizations"
    
    id = Column(Integer, primary_key=True, index=True)
    asin = Column(String, index=True)
    original_title = Column(String)
    optimized_title = Column(String)
    optimization_report = Column(Text)  # AI 生成的优化报告
    keywords_data = Column(JSON)  # 关键词数据
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, nullable=True)
```

---

### 第 2-3 天：AI 选品助手后端 (16h)

#### 任务 2.1: 选品服务实现 (8h)

**文件**: `backend/app/services/ai/product_selection.py`

```python
from typing import Dict, Any, List
from app.services.sorftime import SorftimeClient
from app.services.ai.deepseek_client import DeepSeekClient
from app.services.ai.prompts import PromptTemplates
import logging

logger = logging.getLogger(__name__)

class ProductSelectionService:
    """AI 选品服务"""
    
    def __init__(
        self,
        sorftime_client: SorftimeClient,
        deepseek_client: DeepSeekClient
    ):
        self.sorftime = sorftime_client
        self.ai = deepseek_client
    
    async def analyze_category(
        self,
        category_id: str,
        domain: int = 1
    ) -> Dict[str, Any]:
        """分析类目选品机会"""
        
        # 1. 获取类目数据
        logger.info(f"Fetching category data for {category_id}")
        category_data = await self._fetch_category_data(category_id, domain)
        
        # 2. 构建 AI Prompt
        prompt = self._build_prompt(category_data)
        
        # 3. 调用 AI 分析
        logger.info("Calling DeepSeek API for analysis")
        analysis = await self.ai.chat_completion([
            {"role": "system", "content": "你是一位资深的亚马逊选品专家。"},
            {"role": "user", "content": prompt}
        ])
        
        # 4. 解析结果
        result = {
            "category_id": category_id,
            "category_name": category_data["name"],
            "market_score": self._extract_score(analysis),
            "analysis": analysis,
            "raw_data": category_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return result
    
    async def _fetch_category_data(
        self,
        category_id: str,
        domain: int
    ) -> Dict[str, Any]:
        """获取类目相关数据"""
        
        # 获取类目 Best Sellers
        bestsellers = await self.sorftime.category_request(
            node_id=category_id,
            domain=domain
        )
        
        # 获取类目趋势
        trend = await self.sorftime.category_trend(
            node_id=category_id,
            trend_index=0,  # 销量趋势
            domain=domain
        )
        
        # 获取 Top 10 产品详情
        top_products = []
        if bestsellers.data:
            asins = [p.get('asin') for p in bestsellers.data[:10] if p.get('asin')]
            if asins:
                products_response = await self.sorftime.product_request(
                    asin=','.join(asins),
                    trend=0,
                    domain=domain
                )
                top_products = products_response.data if products_response.data else []
        
        # 计算统计数据
        avg_price = self._calculate_avg_price(top_products)
        avg_rating = self._calculate_avg_rating(top_products)
        
        return {
            "name": category_id,  # TODO: 从 CategoryTree 获取名称
            "bestsellers": bestsellers.data,
            "trend": trend.data,
            "top_products": top_products,
            "avg_price": avg_price,
            "avg_rating": avg_rating
        }
```

#### 任务 2.2: API 端点实现 (4h)

**文件**: `backend/app/api/v1/endpoints/ai.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from app.services.ai.product_selection import ProductSelectionService
from app.services.ai.keyword_optimization import KeywordOptimizationService
from app.schemas.ai import (
    ProductSelectionRequest,
    ProductSelectionResponse,
    KeywordOptimizationRequest,
    KeywordOptimizationResponse
)

router = APIRouter()

@router.post("/product-selection", response_model=ProductSelectionResponse)
async def analyze_product_selection(
    request: ProductSelectionRequest,
    service: ProductSelectionService = Depends(get_product_selection_service)
):
    """AI 选品分析"""
    try:
        result = await service.analyze_category(
            category_id=request.category_id,
            domain=request.domain
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/keyword-optimization", response_model=KeywordOptimizationResponse)
async def optimize_keywords(
    request: KeywordOptimizationRequest,
    service: KeywordOptimizationService = Depends(get_keyword_optimization_service)
):
    """AI 关键词优化"""
    try:
        result = await service.optimize_listing(
            asin=request.asin,
            domain=request.domain
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### 任务 2.3: 缓存和优化 (4h)

- Redis 缓存集成
- 请求去重
- 错误处理和重试

---

### 第 4-5 天：AI 关键词优化后端 (16h)

#### 任务 3.1: 关键词服务实现 (8h)
#### 任务 3.2: API 集成测试 (4h)
#### 任务 3.3: 文档和示例 (4h)

---

### 第 6-8 天：前端实现 (24h)

#### 任务 4.1: AI 选品页面 (12h)

**文件**: `frontend/src/views/ai/ProductSelection.vue`

```vue
<template>
  <div class="product-selection-page">
    <el-card class="header-card">
      <h1>🔍 AI 智能选品助手</h1>
      <p>基于市场数据和 AI 分析，为您推荐高潜力产品</p>
    </el-card>

    <el-card class="input-card">
      <el-form :model="form" label-width="120px">
        <el-form-item label="选择类目">
          <el-cascader
            v-model="form.categoryId"
            :options="categoryTree"
            :props="{ value: 'id', label: 'name', children: 'children' }"
            placeholder="请选择类目"
            filterable
          />
        </el-form-item>
        
        <el-form-item label="站点">
          <el-select v-model="form.domain">
            <el-option label="美国" :value="1" />
            <el-option label="英国" :value="2" />
            <el-option label="德国" :value="3" />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="analyze" :loading="loading">
            🚀 开始分析
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card v-if="result" class="result-card">
      <div class="result-header">
        <h2>📊 分析结果</h2>
        <el-tag type="success" size="large">
          市场机会评分: {{ result.market_score }}/10
        </el-tag>
      </div>
      
      <el-divider />
      
      <div class="markdown-content" v-html="renderedMarkdown"></div>
      
      <el-divider />
      
      <div class="actions">
        <el-button @click="exportReport">导出报告</el-button>
        <el-button @click="saveReport">保存到我的报告</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { analyzeProductSelection } from '@/api/ai'
import { marked } from 'marked'

const form = reactive({
  categoryId: '',
  domain: 1
})

const loading = ref(false)
const result = ref(null)

const renderedMarkdown = computed(() => {
  if (!result.value) return ''
  return marked(result.value.analysis)
})

const analyze = async () => {
  loading.value = true
  try {
    result.value = await analyzeProductSelection(form)
    ElMessage.success('分析完成！')
  } catch (error) {
    ElMessage.error('分析失败：' + error.message)
  } finally {
    loading.value = false
  }
}
</script>
```

#### 任务 4.2: AI 关键词优化页面 (12h)

---

### 第 9-10 天：测试和优化 (16h)

#### 任务 5.1: 单元测试 (8h)
#### 任务 5.2: 集成测试 (4h)
#### 任务 5.3: 性能优化 (4h)

---

## 🧪 测试策略

### 单元测试

```python
# tests/services/ai/test_product_selection.py
import pytest
from app.services.ai.product_selection import ProductSelectionService

@pytest.mark.asyncio
async def test_analyze_category(mock_sorftime_client, mock_deepseek_client):
    service = ProductSelectionService(mock_sorftime_client, mock_deepseek_client)
    result = await service.analyze_category("172282", domain=1)
    
    assert result["category_id"] == "172282"
    assert 1 <= result["market_score"] <= 10
    assert len(result["analysis"]) > 100
```

### 集成测试

```python
# tests/api/test_ai_endpoints.py
def test_product_selection_api(client):
    response = client.post("/api/v1/ai/product-selection", json={
        "category_id": "172282",
        "domain": 1
    })
    assert response.status_code == 200
    assert "market_score" in response.json()
```

---

## 📊 性能目标

| 指标 | 目标 | 说明 |
|------|------|------|
| API 响应时间 | < 30s | 包含 AI 调用 |
| 缓存命中率 | > 70% | 相同查询缓存 24h |
| 并发支持 | 10 QPS | MVP 阶段 |
| AI Token 成本 | < $0.1/次 | 优化 Prompt |

---

## 🔐 安全考虑

1. **API Key 管理**
   - DeepSeek API Key 存储在环境变量
   - 不在日志中记录敏感信息

2. **速率限制**
   - 每用户每天 10 次免费分析
   - 超出需要升级

3. **数据隐私**
   - 不存储用户的 ASIN 数据
   - 分析报告可选择性保存

---

## 📝 环境变量

```bash
# .env
DEEPSEEK_API_KEY=sk-xxx
SORFTIME_API_KEY=xxx
REDIS_URL=redis://localhost:6379
```

---

## 🚀 部署清单

- [ ] 数据库迁移（新表）
- [ ] 环境变量配置
- [ ] Redis 缓存配置
- [ ] 前端路由配置
- [ ] API 文档更新
- [ ] 用户指南编写

---

## 📅 里程碑

- **Day 1**: 基础设施就绪
- **Day 5**: 后端 API 完成
- **Day 8**: 前端页面完成
- **Day 10**: 测试通过，MVP 上线

---

## 🎯 成功标准

- ✅ 能够分析任意类目并生成选品报告
- ✅ 能够优化任意 ASIN 的关键词
- ✅ AI 生成的内容质量高，可直接使用
- ✅ 响应时间满足性能目标
- ✅ 用户反馈积极（>4/5 星）
