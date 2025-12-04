# 开发指南

本指南帮助开发者快速搭建本地开发环境并参与项目开发。

## 开发环境搭建

### 方式一：使用 Docker（推荐）

最简单的方式，无需在本地安装 Python、Node.js 等依赖。

```bash
# 克隆项目
git clone <repository-url>
cd askjeff

# 启动开发环境
make up

# 查看服务状态
make ps
```

服务地址：
- 前端: <http://localhost:5174>
- 后端: <http://localhost:8001>
- API 文档: <http://localhost:8001/docs>
- 数据库: localhost:5433

### 方式二：本地开发

如果需要更好的 IDE 支持和调试体验。

#### 后端开发

```bash
cd backend

# 安装 Poetry
curl -sSL https://install.python-poetry.org | python3 -

# 安装依赖
poetry install

# 启动数据库（使用 Docker）
docker-compose -p askjeff-dev -f ../infra/docker/compose.dev.yml up -d db

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 运行数据库迁移
poetry run alembic upgrade head

# 启动开发服务器
poetry run uvicorn app.main:app --reload --port 8001
```

#### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 项目结构详解

### 后端结构

```
backend/
├── app/
│   ├── api/                 # API 路由
│   │   ├── deps.py         # 依赖注入
│   │   └── routes/         # 路由模块
│   │       ├── imports.py  # 导入相关
│   │       ├── exports.py  # 导出相关
│   │       ├── chat.py     # 聊天相关
│   │       └── ...
│   ├── core/               # 核心功能
│   │   ├── config.py       # 配置管理
│   │   ├── security.py     # 安全相关
│   │   └── errors.py       # 错误处理
│   ├── models/             # SQLAlchemy 模型
│   │   ├── import_batch.py
│   │   ├── export_job.py
│   │   └── ...
│   ├── schemas/            # Pydantic 模式
│   │   ├── imports.py
│   │   ├── exports.py
│   │   └── ...
│   ├── services/           # 业务逻辑
│   │   ├── import_service.py
│   │   ├── export_service.py
│   │   ├── chat_service.py
│   │   ├── deepseek_client.py
│   │   └── ...
│   ├── utils/              # 工具函数
│   ├── db.py              # 数据库连接
│   └── main.py            # 应用入口
├── tests/                  # 测试文件
│   ├── api/               # API 测试
│   ├── services/          # 服务测试
│   └── conftest.py        # 测试配置
├── alembic/               # 数据库迁移
├── storage/               # 文件存储
│   ├── imports/
│   └── exports/
├── pyproject.toml         # Python 依赖
└── pytest.ini             # 测试配置
```

### 前端结构

```
frontend/
├── src/
│   ├── api/               # API 客户端
│   │   ├── http.ts       # Axios 配置
│   │   ├── imports.ts    # 导入 API
│   │   ├── exports.ts    # 导出 API
│   │   └── ...
│   ├── components/        # 公共组件
│   │   ├── ChatBot.vue
│   │   └── ...
│   ├── views/            # 页面视图
│   │   ├── import/
│   │   ├── export/
│   │   ├── chat/
│   │   └── ...
│   ├── stores/           # Pinia 状态管理
│   ├── router/           # Vue Router
│   ├── types/            # TypeScript 类型
│   ├── utils/            # 工具函数
│   ├── App.vue           # 根组件
│   └── main.ts           # 应用入口
├── public/               # 静态资源
├── package.json          # Node 依赖
├── vite.config.ts        # Vite 配置
└── tsconfig.json         # TypeScript 配置
```

## 代码规范

### Python 代码规范

使用 Ruff 进行代码检查和格式化：

```bash
# 检查代码
poetry run ruff check app tests

# 自动修复
poetry run ruff check app tests --fix

# 格式化代码
poetry run ruff format app tests
```

**规范要点**:
- 使用 Type Hints
- 遵循 PEP 8
- 函数和类添加 docstring
- 导入顺序：标准库 → 第三方库 → 本地模块

**示例**:

```python
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services.import_service import import_service


router = APIRouter(prefix="/api/imports", tags=["imports"])


@router.post("", response_model=ImportBatchOut, status_code=201)
async def create_import(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    上传并导入 CSV/XLSX 文件
    
    Args:
        file: 上传的文件
        db: 数据库会话
        
    Returns:
        导入批次信息
    """
    batch = import_service.handle_upload(db, file=file)
    return batch
```

### TypeScript/Vue 代码规范

使用 ESLint 和 Prettier：

```bash
# 检查代码
npm run lint

# 自动修复
npm run lint:fix

# 格式化
npm run format
```

**规范要点**:
- 使用 TypeScript
- 组件使用 `<script setup>` 语法
- Props 和 Emits 使用类型定义
- 使用 Composition API

**示例**:

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getImportList } from '@/api/imports'
import type { ImportBatch } from '@/types/import'

interface Props {
  batchId?: number
}

interface Emits {
  (e: 'update', batch: ImportBatch): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const batches = ref<ImportBatch[]>([])
const loading = ref(false)

const fetchData = async () => {
  loading.value = true
  try {
    const { data } = await getImportList({ page: 1, pageSize: 20 })
    batches.value = data.items
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div class="import-list">
    <el-table :data="batches" :loading="loading">
      <!-- ... -->
    </el-table>
  </div>
</template>
```

## 测试

### 后端测试

```bash
# 运行所有测试
make test-backend

# 或在容器内运行
docker-compose -p askjeff-dev -f infra/docker/compose.dev.yml exec backend \
  poetry run pytest -v

# 运行特定测试
poetry run pytest tests/api/test_imports.py -v

# 查看覆盖率
poetry run pytest --cov=app --cov-report=html tests/
```

**测试结构**:
- `tests/api/` - API 端点测试
- `tests/services/` - 服务层测试
- `tests/models/` - 模型测试

**测试示例**:

```python
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_import():
    """测试创建导入"""
    content = b"ASIN,Title,Price\nB001,Test,10.0"
    response = client.post(
        "/api/imports",
        files={"file": ("test.csv", content, "text/csv")},
        data={"importStrategy": "append"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "test.csv"
    assert data["status"] == "succeeded"
```

### 前端测试

```bash
# 运行单元测试
npm run test:unit

# 运行 E2E 测试
npm run test:e2e
```

## 数据库管理

### 创建迁移

```bash
cd backend

# 自动生成迁移
poetry run alembic revision --autogenerate -m "描述变更"

# 手动创建迁移
poetry run alembic revision -m "描述变更"
```

### 应用迁移

```bash
# 升级到最新版本
poetry run alembic upgrade head

# 回退一个版本
poetry run alembic downgrade -1

# 查看迁移历史
poetry run alembic history
```

### 数据库操作

```bash
# 进入数据库容器
docker-compose -p askjeff-dev -f infra/docker/compose.dev.yml exec db bash

# 连接数据库
psql -U sorftime

# 常用 SQL
\dt                    # 列出所有表
\d table_name          # 查看表结构
SELECT * FROM ...      # 查询数据
```

## 调试技巧

### 后端调试

#### 使用 print/logging

```python
import logging

logger = logging.getLogger(__name__)

def some_function():
    logger.info("调试信息")
    logger.error("错误信息")
```

#### 使用 debugpy（VSCode）

在 `app/main.py` 添加：

```python
if settings.environment == "development":
    import debugpy
    debugpy.listen(("0.0.0.0", 5678))
```

VSCode 配置 `.vscode/launch.json`：

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Remote Attach",
      "type": "python",
      "request": "attach",
      "connect": {
        "host": "localhost",
        "port": 5678
      },
      "pathMappings": [
        {
          "localRoot": "${workspaceFolder}/backend",
          "remoteRoot": "/app"
        }
      ]
    }
  ]
}
```

### 前端调试

使用 Vue DevTools 浏览器扩展：
- Chrome: [Vue.js devtools](https://chrome.google.com/webstore/detail/vuejs-devtools/nhdogjmejiglipccpnnnanhbledajbpd)
- Firefox: [Vue.js devtools](https://addons.mozilla.org/en-US/firefox/addon/vue-js-devtools/)

## 常见问题

### Q: 后端依赖安装失败？

**A**: 清理缓存重试：

```bash
poetry cache clear pypi --all
poetry install
```

### Q: 前端依赖安装失败？

**A**: 清理 node_modules 重试：

```bash
rm -rf node_modules package-lock.json
npm install
```

### Q: 数据库迁移失败？

**A**: 检查数据库连接和迁移文件：

```bash
# 检查数据库连接
poetry run python -c "from app.db import engine; print(engine.url)"

# 查看迁移状态
poetry run alembic current

# 强制标记为已应用（谨慎使用）
poetry run alembic stamp head
```

### Q: 如何重置开发环境？

**A**: 

```bash
# 停止所有服务
make down

# 删除所有数据
docker volume rm askjeff-dev_postgres-data

# 重新启动
make up
```

## Git 工作流

### 分支策略

- `main` - 主分支，保持稳定
- `feature/*` - 功能分支
- `fix/*` - 修复分支
- `docs/*` - 文档分支

### 提交规范

使用 Conventional Commits：

```bash
# 新功能
git commit -m "feat(imports): 添加 Excel 多 sheet 支持"

# 修复 bug
git commit -m "fix(exports): 修复 XLSX 导出编码问题"

# 文档更新
git commit -m "docs: 更新 API 使用示例"

# 重构
git commit -m "refactor(chat): 优化工具调用逻辑"
```

### Pull Request 流程

1. Fork 项目
2. 创建功能分支
3. 编写代码和测试
4. 确保所有测试通过
5. 提交 PR 并描述变更
6. 等待 Code Review
7. 合并到主分支

## 性能优化建议

### 后端优化

1. **数据库查询优化**
   - 使用索引
   - 避免 N+1 查询
   - 使用 `joinedload` 预加载关联

2. **缓存策略**
   - 使用 Redis 缓存热数据
   - 实现查询结果缓存

3. **异步处理**
   - 使用 BackgroundTasks 处理耗时操作
   - 考虑使用 Celery 处理复杂任务

### 前端优化

1. **组件懒加载**

   ```typescript
   const ImportView = () => import('@/views/import/index.vue')
   ```

2. **虚拟滚动**
   - 大列表使用虚拟滚动组件

3. **请求优化**
   - 实现请求去重
   - 使用防抖和节流

## 更多资源

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Vue 3 文档](https://vuejs.org/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [Element Plus 文档](https://element-plus.org/)
- [项目需求文档](../specs/README.md)
