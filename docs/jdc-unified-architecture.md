# Jeff Data Core (JDC) 统一数据层架构设计

## 🎯 核心理念

**JDC = 统一数据层**

```
应用程序层（业务逻辑）
         ↓
    Jeff Data Core (JDC)  ← 所有数据调用都在这里
         ↓
   数据层（API、AI、存储）
```

**设计目标**:
1. 应用程序只与 JDC 交互
2. 所有外部 API 调用都在 JDC
3. 所有 AI 功能都在 JDC
4. JDC 是唯一的数据入口

---

## 🏗️ 新的 JDC 架构

### 模块结构

```
backend/packages/jeff-data-core/
├─ jeff_data_core/
│  ├─ __init__.py
│  ├─ config.py              # 配置管理
│  ├─ core/
│  │  ├─ __init__.py
│  │  └─ engine.py         # 核心引擎（保持）
│  ├─ connectors/            # API 连接器（扩展）
│  │  ├─ __init__.py
│  │  ├─ base.py
│  │  ├─ amazon_ads.py      # Amazon Ads API (已有）
│  │  ├─ amazon_sp.py       # Amazon SP-API (新增）
│  │  ├─ sorftime.py        # Sorftime API (新增)
│  │  ├─ shopify.py        # Shopify API (未来)
│  │  └─ ...
│  ├─ ai/                   # AI 模块（新增）
│  │  ├─ __init__.py
│  │  ├─ base.py           # AI 基类
│  │  ├─ deepseek.py        # DeepSeek (迁移)
│  │  ├─ openai.py         # OpenAI (未来)
│  │  └─ ...
│  ├─ normalizers/          # 数据规范化器（已有）
│  │  ├─ base.py
│  │  ├─ amazon_ads.py
│  │  └─ ...
│  ├─ storage/             # 存储层（已有）
│  │  ├─ base.py
│  │  └─ postgres.py
│  └─ models.py            # 数据模型（已有）
└─ pyproject.toml
```

---

## 📋 API 连接器设计

### 基类

```python
class BaseConnector(ABC):
    """所有 API 连接器的基类"""

    @abstractmethod
    def fetch_data(self, **kwargs) -> Iterator[Dict]:
        """获取数据"""

    @abstractmethod
    def validate_credentials(self) -> bool:
        """验证凭证"""
```

### Amazon Ads Connector (已有)

```python
class AmazonAdsConnector(BaseConnector):
    """Amazon Advertising API"""
    # 已实现
```

### Amazon SP-API Connector (新增)

```python
class AmazonSPConnector(BaseConnector):
    """Amazon Selling Partner API

    用于获取:
    - 库存报告 (FBA Inventory)
    - 业务报告 (Business Reports)
    - 订单数据 (Orders)
    - 产品数据 (Catalog)
    """

    def __init__(self, config: AmazonSPConfig):
        self.config = config
        self.client = httpx.Client(...)

    def fetch_inventory_report(
        self, start_date: date, end_date: date
    ) -> Iterator[Dict]:
        """获取库存报告"""
        # 调用 Amazon SP-API
        pass

    def fetch_business_report(
        self, start_date: date, end_date: date
    ) -> Iterator[Dict]:
        """获取业务报告"""
        # 调用 Amazon SP-API
        pass
```

### Sorftime Connector (新增）

```python
class SorftimeConnector(BaseConnector):
    """Sorftime API 连接器

    用于获取市场数据:
    - 产品列表
    - 产品详情
    - 市场趋势
    - 竞品分析
    """

    def __init__(self, config: SorftimeConfig):
        self.config = config
        self.client = httpx.Client(...)

    def fetch_products(self, asin: str) -> Dict:
        """获取产品详情"""
        # 调用 Sorftime API
        pass

    def search_products(
        self, keyword: str, filters: Dict
    ) -> Iterator[Dict]:
        """搜索产品"""
        # 调用 Sorftime API
        pass

    def fetch_trends(self, category: str) -> List[Dict]:
        """获取市场趋势"""
        # 调用 Sorftime API
        pass
```

---

## 🤖 AI 模块设计

### 基类

```python
class BaseAIProvider(ABC):
    """所有 AI 提供商的基类"""

    @abstractmethod
    def chat(self, messages: List[Dict]) -> str:
        """对话接口"""

    @abstractmethod
    def extract_features(self, data: List[Dict]) -> Dict:
        """特征提取"""

    @abstractmethod
    def analyze(self, data: Any) -> str:
        """数据分析"""
```

### DeepSeek Provider (从 app 迁移）

```python
class DeepSeekAIProvider(BaseAIProvider):
    """DeepSeek AI 提供商"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.Client(...)

    def chat(self, messages: List[Dict]) -> str:
        """对话"""
        # 调用 DeepSeek Chat API
        pass

    def extract_features(self, products: List[Dict]) -> Dict:
        """产品特征提取"""
        # 调用 DeepSeek API
        pass

    def analyze_ads(self, ads_data: Dict) -> str:
        """广告诊断"""
        # 调用 DeepSeek API
        pass
```

### OpenAI Provider (未来)

```python
class OpenAIProvider(BaseAIProvider):
    """OpenAI 提供商"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.Client(...)

    def chat(self, messages: List[Dict]) -> str:
        """对话"""
        pass
```

---

## 🏢 JDC 统一接口

### JeffDataEngine (扩展）

```python
class JeffDataEngine:
    """统一数据引擎"""

    def __init__(self, config: EngineConfig):
        self.storage = PostgresStorage(config.db_url)

        # 初始化 API 连接器
        self.api_connectors: Dict[str, BaseConnector] = {
            'amazon_ads': AmazonAdsConnector(config.amazon_ads),
            'amazon_sp': AmazonSPConnector(config.amazon_sp),
            'sorftime': SorftimeConnector(config.sorftime),
            'shopify': ShopifyConnector(config.shopify),
        }

        # 初始化 AI 提供商
        self.ai_providers: Dict[str, BaseAIProvider] = {
            'deepseek': DeepSeekAIProvider(config.deepseek_api_key),
            'openai': OpenAIProvider(config.openai_api_key),
        }

    # API 方法
    def fetch_data(
        self, source: str, method: str, **kwargs
    ) -> Iterator[Dict]:
        """获取数据

        示例:
        engine.fetch_data('amazon_sp', 'inventory_report', start_date=..., end_date=...)
        engine.fetch_data('sorftime', 'search_products', keyword='...')
        """
        connector = self.api_connectors[source]
        return connector.fetch_data(method, **kwargs)

    def sync_data(
        self, source: str, start_date: date, end_date: date
    ) -> Dict[str, Any]:
        """同步数据"""
        connector = self.api_connectors[source]
        return self.run_sync(connector, start_date, end_date)

    # AI 方法
    def chat(self, provider: str, messages: List[Dict]) -> str:
        """AI 对话

        示例:
        engine.chat('deepseek', [{'role': 'user', 'content': '...'}])
        """
        ai = self.ai_providers[provider]
        return ai.chat(messages)

    def extract_features(
        self, provider: str, data: List[Dict]
    ) -> Dict:
        """AI 特征提取

        示例:
        engine.extract_features('deepseek', products)
        """
        ai = self.ai_providers[provider]
        return ai.extract_features(data)

    def analyze_ads(self, provider: str, data: Dict) -> str:
        """AI 广告诊断

        示例:
        engine.analyze_ads('deepseek', ads_data)
        """
        ai = self.ai_providers[provider]
        return ai.analyze(data)
```

---

## 🔄 迁移计划

### Phase 1: Amazon SP-API Connector (1 周)

**任务**:
1. 创建 `amazon_sp.py` Connector
2. 实现 OAuth 认证
3. 实现库存报告获取
4. 实现业务报告获取
5. 编写单元测试

**迁移**:
- 从 `AmazonSyncService` 迁移逻辑到 JDC
- 更新 `AmazonSyncService` 使用 JDC

---

### Phase 2: AI 模块迁移 (1 周)

**任务**:
1. 创建 AI 基类
2. 迁移 `chat_service.py` 的 DeepSeek 调用到 JDC
3. 迁移 `extraction_service.py` 的 AI 调用到 JDC
4. 迁移 `ads_analysis_service.py` 的 AI 调用到 JDC
5. 迁移 `ads_diagnosis_service.py` 的 AI 调用到 JDC
6. 编写单元测试

**删除**:
- `backend/app/services/chat_service.py`
- `backend/app/services/extraction_service.py` (保留业务逻辑)
- DeepSeek 相关的客户端代码

---

### Phase 3: Sorftime Connector (1 周)

**任务**:
1. 创建 `sorftime.py` Connector
2. 迁移 `SorftimeClient` 到 JDC
3. 实现 API 方法
4. 编写单元测试

**迁移**:
- 从 `backend/app/services/sorftime/` 迁移到 JDC
- 更新 `APIImportService` 使用 JDC

---

### Phase 4: 统一应用层 (1-2 周)

**任务**:
1. 重构所有 Service 使用 JDC
2. 删除直接调用 API 的代码
3. 更新配置管理
4. 编写集成测试

**重构**:
```python
# Before
class SomeService:
    def process(self):
        client = SorftimeClient(...)
        data = client.fetch_products(...)
        ai = DeepSeekClient(...)
        result = ai.analyze(data)

# After
class SomeService:
    def __init__(self):
        self.engine = JeffDataEngine(config)

    def process(self):
        data = self.engine.fetch_data('sorftime', 'search_products', keyword='...')
        result = self.engine.analyze('deepseek', data)
```

---

## 📊 架构优势

### 对应用层
✅ **统一接口**
   - 应用只与 JDC 交互
   - 不关心数据来源
   - 不关心 AI 提供商

✅ **易于切换**
   - 切换 API 提供商：修改配置即可
   - 切换 AI 提供商：修改配置即可

✅ **便于测试**
   - 可以 Mock JDC 进行测试
   - 可以注入不同的实现

### 对 JDC 层
✅ **职责清晰**
   - API 调用统一在 JDC
   - AI 功能统一在 JDC
   - 数据转换统一在 JDC

✅ **便于扩展**
   - 新增 API：添加 Connector
   - 新增 AI：添加 Provider
   - 不影响应用层

✅ **便于维护**
   - 所有外部依赖集中管理
   - 版本升级只在 JDC 中
   - 统一的错误处理

---

## 📝 配置设计

### EngineConfig

```python
@dataclass
class EngineConfig:
    """JDC 统一配置"""

    # 数据库
    db_url: str

    # Amazon Ads
    amazon_ads_client_id: str
    amazon_ads_client_secret: str
    amazon_ads_refresh_token: str

    # Amazon SP-API
    amazon_sp_client_id: str
    amazon_sp_client_secret: str
    amazon_sp_refresh_token: str

    # Sorftime
    sorftime_api_key: str
    sorftime_base_url: str = "https://api.sorftime.com"

    # AI 提供商
    deepseek_api_key: str
    openai_api_key: Optional[str] = None
    default_ai_provider: str = "deepseek"

    # 连接池
    max_connections: int = 10
    timeout: int = 30
```

---

## 🎯 实施建议

### 立即开始 (本周)

**采用这个方案，理由是**:
1. 符合你的想法：所有数据调用都在 JDC
2. 包含 API 和 AI 功能
3. 应用程序只与 JDC 交互

**第一步**:
1. 设计详细的 API
2. 实现 Amazon SP-API Connector (Phase 1)
3. 实现 AI 基类和 DeepSeek Provider (Phase 2)

**预期效果**:
- JDC 成为真正的统一数据层
- 应用层代码大幅简化
- 架构清晰易于维护

---

## ❓ 需要确认

1. **迁移优先级**:
   - 先做 API Connector？
   - 先做 AI Provider？
   - 并行进行？

2. **迁移范围**:
   - 所有 AI 调用都迁移到 JDC？
   - 所有 API 调用都迁移到 JDC？

3. **时间安排**:
   - 预计多久完成？
   - 是否允许影响现有功能？

---

## 📋 总结

**新架构**:
```
应用层 (业务逻辑)
         ↓
    Jeff Data Core (JDC)
         ├─ Connectors (API 调用)
         ├─ AI Providers (AI 功能)
         └─ Storage (数据存储)
         ↓
      外部服务
```

**核心原则**:
- 应用只与 JDC 交互
- 所有的数据调用都在 JDC
- JDC 是唯一的数据入口

这是一个更加统一和清晰的架构！
