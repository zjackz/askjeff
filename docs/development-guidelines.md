# 开发规范指南

**项目**: ASKJeff - Amazon Ads Analysis  
**适用范围**: 所有功能开发  
**版本**: v1.0  
**最后更新**: 2025-12-31

---

## 📐 代码规范

### Python 代码规范 (PEP8)

#### 1. 命名规范

```python
# ✅ 正确示例

# 类名: PascalCase
class AmazonSyncService:
    pass

# 函数名: snake_case
def sync_inventory_data():
    pass

# 变量名: snake_case
store_id = uuid4()
sync_task = SyncTask()

# 常量: UPPER_SNAKE_CASE
MAX_RETRY_COUNT = 3
DEFAULT_SYNC_DAYS = 30

# 私有方法/变量: 前缀 _
def _parse_report_data():
    pass
```

#### 2. 类型提示

```python
# ✅ 必须使用类型提示

from typing import List, Dict, Optional
from uuid import UUID
from datetime import date

def sync_inventory(
    store_id: UUID,
    days: int = 30,
    force: bool = False
) -> SyncTask:
    """同步库存数据"""
    pass

def get_sync_tasks(
    store_id: UUID,
    status: Optional[str] = None
) -> List[SyncTask]:
    """获取同步任务列表"""
    pass
```

#### 3. 文档字符串 (Google Style)

```python
# ✅ 完整的文档字符串

def sync_inventory(store_id: UUID, days: int = 30) -> SyncTask:
    """同步 Amazon 库存数据
    
    从 Amazon SP-API 获取库存报告并保存到数据库。
    支持增量同步,已存在的数据会被更新。
    
    Args:
        store_id: 店铺 UUID
        days: 同步天数,默认 30 天
        
    Returns:
        SyncTask: 同步任务对象
        
    Raises:
        ValueError: 店铺不存在或未激活
        APIError: Amazon API 调用失败
        
    Example:
        >>> service = AmazonSyncService(db)
        >>> task = service.sync_inventory(store_id, days=7)
        >>> print(task.status)
        'success'
    """
    pass
```

#### 4. 错误处理

```python
# ✅ 明确的异常处理

class AmazonAPIError(Exception):
    """Amazon API 错误基类"""
    pass

class InvalidCredentialsError(AmazonAPIError):
    """API 凭证无效"""
    pass

class RateLimitError(AmazonAPIError):
    """API 限流"""
    pass

# 使用具体的异常
def get_access_token(self) -> str:
    try:
        response = requests.post(...)
        response.raise_for_status()
        return response.json()["access_token"]
    except requests.HTTPError as e:
        if e.response.status_code == 401:
            raise InvalidCredentialsError("Invalid refresh token")
        elif e.response.status_code == 429:
            raise RateLimitError("API rate limit exceeded")
        else:
            raise AmazonAPIError(f"API error: {e}")
```

---

## 🧪 测试规范

### 1. 测试文件组织

```
tests/
├── conftest.py                 # 共享 fixtures
├── unit/                       # 单元测试
│   ├── test_sp_api_client.py
│   └── test_sync_service.py
├── integration/                # 集成测试
│   └── test_sync_workflow.py
└── performance/                # 性能测试
    └── test_sync_performance.py
```

### 2. 测试命名规范

```python
# ✅ 清晰的测试命名

class TestInventorySync:
    """库存同步测试"""
    
    def test_sync_inventory_success(self):
        """测试库存同步成功"""
        pass
    
    def test_sync_inventory_with_invalid_credentials(self):
        """测试 API 凭证无效时的处理"""
        pass
    
    def test_sync_inventory_incremental_update(self):
        """测试增量更新"""
        pass
```

### 3. AAA 模式

```python
# ✅ Arrange-Act-Assert 模式

def test_sync_inventory_success(self, db, mock_store):
    # Arrange (准备)
    mock_data = [{"sku": "TEST-001", "quantity": 100}]
    service = AmazonSyncService(db)
    
    with patch('...fetch_inventory_report') as mock_fetch:
        mock_fetch.return_value = mock_data
        
        # Act (执行)
        task = service.sync_inventory(mock_store.id)
        
        # Assert (断言)
        assert task.status == "success"
        assert task.records_synced == 1
```

### 4. Fixture 使用

```python
# ✅ 可复用的 fixtures

@pytest.fixture
def mock_amazon_store(db):
    """创建测试店铺"""
    store = AmazonStore(
        id=uuid4(),
        store_name="Test Store",
        ...
    )
    db.add(store)
    db.commit()
    return store

@pytest.fixture
def mock_inventory_data():
    """Mock 库存数据"""
    return [
        {"sku": "SKU-001", "quantity": 100},
        {"sku": "SKU-002", "quantity": 200},
    ]
```

---

## 📝 文档规范

### 1. 需求文档模板

```markdown
# Feature XXX: 功能名称

**功能编号**: ADS-XXX
**优先级**: P0/P1/P2
**预计工作量**: X 天

## 需求概述
- 业务背景
- 目标用户
- 核心价值

## 功能需求
### FR-001: 功能点 1
- 描述
- 输入/输出
- 业务规则
- API 端点

## 技术设计
- 系统架构
- 核心类设计
- 数据库设计

## 测试用例
### TC-001: 测试场景 1
- 前置条件
- 测试步骤
- 预期结果

## 验收标准
- 功能验收
- 性能验收
- 质量验收
```

### 2. API 文档规范

```python
# ✅ 使用 FastAPI 自动生成文档

@router.post(
    "/stores/{store_id}/sync/inventory",
    response_model=SyncTaskSchema,
    summary="同步库存数据",
    description="从 Amazon SP-API 同步库存数据到数据库",
    responses={
        200: {"description": "同步任务创建成功"},
        404: {"description": "店铺不存在"},
        409: {"description": "同步任务已在运行"},
    }
)
async def sync_inventory(
    store_id: UUID,
    days: int = Query(30, ge=1, le=90, description="同步天数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> SyncTaskSchema:
    """
    同步库存数据
    
    从 Amazon SP-API 获取 FBA 库存报告并保存到数据库。
    
    - **store_id**: 店铺 UUID
    - **days**: 同步天数 (1-90)
    """
    pass
```

---

## 🔄 Git 工作流

### 1. 分支命名

```bash
# 功能分支
feature/ads-001-data-sync
feature/ads-002-cost-management

# 修复分支
fix/sync-task-retry-logic
fix/api-error-handling

# 热修复分支
hotfix/critical-sync-bug
```

### 2. 提交信息规范

```bash
# ✅ 清晰的提交信息

# 格式: <type>(<scope>): <subject>

feat(sync): 实现 SP-API 库存数据同步
fix(sync): 修复并发同步导致的数据重复
docs(sync): 更新 API 文档
test(sync): 添加库存同步单元测试
refactor(sync): 重构错误处理逻辑
perf(sync): 优化批量插入性能

# Type 类型:
# - feat: 新功能
# - fix: 修复 bug
# - docs: 文档更新
# - test: 测试相关
# - refactor: 重构
# - perf: 性能优化
# - chore: 构建/工具相关
```

### 3. Pull Request 规范

```markdown
## 功能描述
实现 Amazon 库存数据自动同步功能

## 变更内容
- 添加 SP-API 客户端
- 实现库存同步服务
- 添加 Celery 定时任务
- 编写单元测试

## 测试
- [x] 单元测试通过 (覆盖率 85%)
- [x] 集成测试通过
- [x] 性能测试通过 (1000 SKU < 5min)

## 相关文档
- 需求文档: feature-001-data-sync.md
- API 文档: /api/docs

## 截图
(如有 UI 变更,添加截图)

## Checklist
- [x] 代码符合规范
- [x] 测试覆盖充分
- [x] 文档已更新
- [x] 无 lint 错误
```

---

## 🏗️ 项目结构规范

### 后端结构

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   │           └── amazon_sync.py
│   ├── clients/
│   │   └── amazon/
│   │       ├── base_client.py
│   │       ├── sp_api_client.py
│   │       └── ads_api_client.py
│   ├── models/
│   │   └── amazon_ads.py
│   ├── schemas/
│   │   └── amazon_ads.py
│   ├── services/
│   │   └── amazon_sync_service.py
│   ├── tasks/
│   │   └── sync_tasks.py
│   ├── celery_app.py
│   └── main.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── alembic/
│   └── versions/
├── pyproject.toml
└── README.md
```

### 前端结构

```
frontend/
├── src/
│   ├── views/
│   │   └── ads-analysis/
│   │       ├── index.vue
│   │       ├── MatrixView.vue
│   │       └── components/
│   │           ├── SyncStatus.vue
│   │           └── StoreSelector.vue
│   ├── api/
│   │   └── amazon-sync.ts
│   ├── types/
│   │   └── amazon.ts
│   └── utils/
│       └── http.ts
└── tests/
    └── unit/
```

---

## 📊 代码审查检查清单

### 功能性

- [ ] 功能符合需求文档
- [ ] 边界条件处理正确
- [ ] 错误处理完善
- [ ] 日志记录充分

### 代码质量

- [ ] 代码符合规范
- [ ] 命名清晰易懂
- [ ] 无重复代码
- [ ] 复杂度合理

### 测试

- [ ] 单元测试覆盖 > 80%
- [ ] 测试用例充分
- [ ] 所有测试通过
- [ ] 无测试警告

### 安全性

- [ ] 无 SQL 注入风险
- [ ] 敏感数据加密
- [ ] 权限验证正确
- [ ] 输入验证完善

### 性能

- [ ] 无 N+1 查询
- [ ] 批量操作优化
- [ ] 缓存使用合理
- [ ] 资源释放正确

### 文档

- [ ] API 文档完整
- [ ] 代码注释充分
- [ ] README 更新
- [ ] CHANGELOG 更新

---

## 🎯 质量标准

### 代码质量指标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 测试覆盖率 | > 80% | 单元测试 + 集成测试 |
| 代码复杂度 | < 10 | McCabe 复杂度 |
| 重复代码 | < 3% | 代码重复率 |
| 文档覆盖率 | 100% | 公共 API 必须有文档 |
| Lint 错误 | 0 | 无 Ruff/Pylint 错误 |

### 性能标准

| 指标 | 目标值 |
|------|--------|
| API 响应时间 (P95) | < 200ms |
| 数据库查询时间 | < 100ms |
| 同步任务成功率 | > 95% |
| 系统可用性 | > 99.9% |

---

**遵循这些规范,确保代码质量和项目可维护性! ✅**

---

**版本**: v1.0  
**最后更新**: 2025-12-31
