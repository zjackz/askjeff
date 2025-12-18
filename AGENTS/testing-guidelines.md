# AI 测试策略规范（模板）

> 建议放置位置：项目根目录 `AGENTS/`（便于跨项目复制）。

## MUST（测试覆盖底线）

### ⚠️ 重要：所有新功能必须编写单元测试，测试通过后才能提交

### 测试覆盖要求

- ✅ 新增 API 端点必须有对应的集成测试
- ✅ 核心业务逻辑（Service 层）必须有单元测试
- ✅ 复杂的数据处理逻辑必须有测试用例
- ✅ 所有测试必须通过才能推送代码

### 测试类型优先级

1. **集成测试** - API 端点的端到端测试
2. **单元测试** - 业务逻辑、工具函数的独立测试
3. **边界测试** - 异常输入、边界条件的测试
4. **性能测试** - 关键路径的性能基准（可选）

## 后端测试

### 配置说明

#### 测试框架与工具

- **单元测试**: pytest
- **API 测试**: FastAPI TestClient
- **集成测试**: Mock 外部服务（如 DeepSeek API、Sorftime API）
- **数据库测试**: 使用测试数据库（Docker 环境自动配置）
- **运行环境**: 推荐在 Docker 容器中运行测试以确保环境一致性

### 运行测试命令

```bash
# 在 Docker 中运行所有测试
docker exec askjeff-dev-backend-1 poetry run pytest tests/

# 运行特定测试文件
docker exec askjeff-dev-backend-1 poetry run pytest tests/api/test_extraction.py

# 查看测试覆盖率
docker exec askjeff-dev-backend-1 poetry run pytest --cov=app tests/

# 本地运行测试（仅当 Docker 不可用时）
cd backend && poetry run pytest tests/
```

#### 测试文件组织

```text
tests/
├── unit/              # 单元测试
│   ├── services/      # Service 层测试
│   └── utils/         # 工具函数测试
├── integration/       # 集成测试
│   └── api/           # API 端点测试
└── fixtures/          # 测试数据和 fixtures
```

## 前端测试

### 配置说明

#### 测试类型

- **静态检查**: ESLint / TypeScript 类型检查
- **中文合规检查**: 确保代码、注释、文档使用中文
- **单元测试**: 组件逻辑测试（可选）
- **E2E 测试**: 关键用户流程测试（可选）

#### 运行测试命令

```bash
# 前端 Lint
pnpm --prefix frontend lint

# 类型检查
pnpm --prefix frontend type-check

# 中文合规检查
python scripts/check_cn.py
```

## 测试编写规范

### 单元测试示例

```python
# tests/unit/services/test_example_service.py
import pytest
from app.services.example_service import ExampleService

class TestExampleService:
    """示例服务测试"""
    
    def test_success_case(self):
        """测试成功场景"""
        result = ExampleService.process_data(valid_input)
        assert result.status == "success"
        assert result.data is not None
    
    def test_invalid_input(self):
        """测试无效输入"""
        with pytest.raises(ValueError):
            ExampleService.process_data(invalid_input)
    
    def test_edge_case(self):
        """测试边界条件"""
        result = ExampleService.process_data(edge_case_input)
        assert result.status == "warning"
```

### API 集成测试示例

```python
# tests/integration/api/test_example_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestExampleAPI:
    """示例 API 测试"""
    
    def test_get_endpoint(self):
        """测试 GET 端点"""
        response = client.get("/api/v1/example")
        assert response.status_code == 200
        assert "data" in response.json()
    
    def test_post_endpoint_success(self):
        """测试 POST 端点成功场景"""
        payload = {"key": "value"}
        response = client.post("/api/v1/example", json=payload)
        assert response.status_code == 201
    
    def test_post_endpoint_validation_error(self):
        """测试 POST 端点验证失败"""
        invalid_payload = {"invalid": "data"}
        response = client.post("/api/v1/example", json=invalid_payload)
        assert response.status_code == 422
```

## Mock 外部服务

### 原则

- ✅ 所有外部 API 调用必须 Mock
- ✅ Mock 数据应接近真实响应
- ✅ 测试成功和失败两种场景
- ✅ 记录 Mock 的假设和限制

### 示例

```python
from unittest.mock import patch, MagicMock

@patch('app.services.external_api_client.ExternalAPIClient.fetch_data')
def test_with_mocked_api(mock_fetch):
    """使用 Mock 外部 API 的测试"""
    # 设置 Mock 返回值
    mock_fetch.return_value = {
        "code": 200,
        "data": {"key": "value"}
    }
    
    # 执行测试
    result = MyService.process_external_data()
    
    # 验证结果
    assert result.success is True
    mock_fetch.assert_called_once()
```

## 测试数据管理

### Fixtures

```python
# tests/fixtures/example_fixtures.py
import pytest

@pytest.fixture
def sample_user():
    """示例用户数据"""
    return {
        "id": 1,
        "username": "test_user",
        "email": "test@example.com"
    }

@pytest.fixture
def db_session():
    """测试数据库会话"""
    # 创建测试数据库连接
    session = create_test_db_session()
    yield session
    # 清理
    session.rollback()
    session.close()
```

## 持续集成（CI）门禁

### 提交前必须通过

```bash
# 1. 运行所有测试
docker exec askjeff-dev-backend-1 poetry run pytest tests/

# 2. 静态检查
pnpm --prefix frontend lint
cd backend && poetry run ruff check

# 3. 类型检查（如适用）
pnpm --prefix frontend type-check

# 4. 中文合规检查
python scripts/check_cn.py
```

### CI 流程（项目占位符）

```yaml
# 示例 CI 配置
test:
  - run: <backend-test-command>
  - run: <frontend-lint-command>
  - run: <cn-check-command>
```

## 测试覆盖率目标

### askjeff 项目配置

- **核心业务逻辑**: ≥ 80%
- **API 端点**: ≥ 90%
- **工具函数**: ≥ 70%
- **整体覆盖率**: ≥ 60%
