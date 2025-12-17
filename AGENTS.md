# askjeff 开发规范

AI 代理开发指南 - 技术栈、编码标准与工作流程

**最后更新**: 2025-11-29

> 📋 **需求管理**: 查看 [specs/README.md](specs/README.md) 了解需求管理和开发工作流程  
> 🚀 **快速开始**: 使用 `/new-requirement` 创建新需求

---

## 技术栈

### 前端
- **框架**: Vue 3 + TypeScript + Vite
- **UI 组件库**: Vue Element Admin (基于 Element Plus)
- **状态管理**: Pinia
- **路由**: Vue Router
- **图表**: ECharts
- **包管理**: pnpm

### 后端
- **框架**: FastAPI (Python 3.12+)
- **数据验证**: Pydantic v2
- **ORM**: SQLAlchemy 2.0
- **数据库迁移**: Alembic
- **HTTP 客户端**: HTTPX
- **异步任务**: FastAPI BackgroundTasks
- **外部 API**: Deepseek API（自然语言查询）

### 数据存储
- **数据库**: PostgreSQL 15
- **文件存储**: 本地挂载目录 `backend/storage/`（导入/导出文件）

### DevOps
- **容器化**: Docker + Docker Compose
- **开发环境**: 必须使用 Docker Compose（热更新），禁止本地直接运行后端服务
- **生产部署**: systemd 管理 Docker Compose stack
- **日志**: Python logging
- **指标**: 脚本导出 CSV
- **强制要求**: 所有后端开发、测试必须在 Docker 容器中进行，避免本地环境差异导致的问题

---

## 项目结构

```text
askjeff/
├── frontend/              # Vue Element Admin 前端
│   ├── src/
│   │   ├── components/   # 可复用组件
│   │   ├── views/        # 页面视图
│   │   ├── router/       # 路由配置
│   │   ├── stores/       # Pinia 状态管理
│   │   └── api/          # API 调用
│   └── package.json
│
├── backend/               # FastAPI 后端
│   ├── app/
│   │   ├── main.py       # FastAPI 应用入口
│   │   ├── config.py     # 配置管理
│   │   ├── db.py         # 数据库连接
│   │   ├── models/       # SQLAlchemy 数据模型
│   │   ├── schemas/      # Pydantic 数据验证
│   │   ├── services/     # 业务逻辑层
│   │   ├── api/
│   │   │   ├── deps.py   # 依赖注入
│   │   │   └── routes/   # API 路由
│   │   └── utils/        # 工具函数
│   ├── tests/            # 测试文件
│   ├── migrations/       # Alembic 数据库迁移
│   └── storage/          # 文件存储（导入/导出）
│
├── infra/
│   └── docker/           # Docker Compose 配置
│
├── specs/                # 需求规格文档
│   ├── README.md         # 需求索引与工作流程
│   ├── BACKLOG.md        # 需求池
│   ├── 001-sorftime-data-console/
│   ├── 002-insight-product-list/
│   └── 003-product-feature-extraction/
│
├── .agent/
│   └── workflows/        # 工作流程定义
│
└── scripts/              # 工具脚本
```

---

## 开发工作流

### 创建新需求

使用简化的工作流程，所有开发在 `main` 分支进行：

```bash
# 1. 在 AI 助手中运行
/new-requirement

# 2. AI 会自动：
#    - 将需求文档迁移到 specs/00X-feature-name/
#    - 创建 spec.md, plan.md, tasks.md
#    - 更新 specs/README.md 注册新需求

# 3. 开始实施
#    AI 会按照 tasks.md 逐步实现功能

# 4. 提交到 main 分支
git add .
git commit -m "feat(00X): 功能描述"
git push origin main
```

详细流程参见 [.agent/workflows/new-requirement.md](.agent/workflows/new-requirement.md)

### 分支策略

- **主分支**: `main` - 所有开发直接在此进行
- **临时分支**: 仅在大型重构或实验性功能时创建，完成后立即合并删除
- **备份分支**: `backup/*` - 保留历史快照

### 验证与推送流程

完成功能开发后，必须执行以下验证和推送流程：

#### 1. 代码验证

**⚠️ 重要：所有新功能必须编写单元测试，测试通过后才能提交**

```bash
# 前端验证
pnpm --prefix frontend lint

# 后端验证（在 Docker 中）
docker exec askjeff-dev-backend-1 poetry run pytest tests/
docker exec askjeff-dev-backend-1 poetry run ruff check

# 或本地验证
cd backend && poetry run pytest tests/ && poetry run ruff check
```

**测试覆盖要求**：
- ✅ 新增 API 端点必须有对应的集成测试
- ✅ 核心业务逻辑（Service 层）必须有单元测试
- ✅ 复杂的数据处理逻辑必须有测试用例
- ✅ 所有测试必须通过才能推送代码

#### 2. Git 推送流程

```bash
# 拉取最新代码
git pull

# 添加所有修改
git add .

# 提交修改（使用规范的提交信息）
git commit -m "feat(003): 添加 LLM 产品特征提取功能"
# 或
git commit -m "fix(002): 修复导入编码问题"
# 或
git commit -m "docs: 更新 AGENTS.md 开发规范"

# 推送到远程
git push
```

#### 3. 提交信息规范

- `feat(编号): 描述` - 新功能
- `fix(编号): 描述` - Bug 修复
- `docs: 描述` - 文档更新
- `test: 描述` - 测试相关
- `refactor: 描述` - 代码重构
- `chore: 描述` - 构建/工具变更

---

## 常用命令

### 开发环境

```bash
# 启动所有服务（Docker Compose）
make up
# 或
docker compose -f infra/docker/compose.yml up -d

# 查看服务状态
make ps

# 查看日志
make backend-logs
make frontend-logs

# 停止服务
make down
```

### 代码质量检查

```bash
# 前端 Lint
pnpm --prefix frontend lint

# 后端测试（Docker 环境）
docker exec askjeff-dev-backend-1 poetry run pytest tests/

# 后端测试（本地环境）
cd backend && poetry run pytest tests/

# 后端静态检查
cd backend && poetry run ruff check

# 全仓中文合规检查
python scripts/check_cn.py
```

### 指标与监控

```bash
# 生成导入/问答/导出指标 CSV
python scripts/report_metrics.py --days 7
```

---

## 编码规范

### 通用规范

- ✅ **所有代码、注释、Commit 与文档必须使用中文**
  - 保留必要的技术术语（如 API、HTTP、JSON）
  - 技术术语首次出现时附中文解释
- ✅ **提交信息格式**: `feat(编号): 功能描述` 或 `fix(编号): 修复描述`
- ✅ **小步提交**: 每完成一个小功能就提交一次

### 前端规范（Vue 3）

- 使用 `<script setup>` + Composition API
- 组件命名采用 PascalCase（如 `UserProfile.vue`）
- Element Plus 组件保持中文文案
- 状态管理优先使用 Pinia
- API 调用统一封装在 `src/api/` 目录
- **UI 尺寸规范**:
  - **全局尺寸**: Element Plus 使用默认尺寸 (`size="default"`)。
  - **避免硬编码**: 严禁在按钮、输入框等组件上硬编码 `size="small"`，除非在极紧凑的上下文中（如表格行内操作）。
- **表格 UI 规范**:
  - **布局**: 使用全屏 Flex 布局，表格高度自适应 (`height="100%"`)，避免页面滚动条。
  - **样式**: 跟随全局默认尺寸，确保行高适中，提升可读性。
  - **分页**: 必须提供 `page-sizes` 选项 `[20, 50, 100, 200]`，默认每页 50 条。
  - **容器**: 表格应包裹在 `.table-container` 中，设置圆角和阴影。

### 后端规范（FastAPI）

- 模块拆分：
  - `api/routers` - 路由定义
  - `services` - 业务逻辑
  - `models` - 数据模型
  - `schemas` - 数据验证
- 使用 BackgroundTasks 处理导入/导出，无需单独 Celery worker
- 所有 API 端点必须有类型注解和文档字符串
- 使用 Pydantic v2 进行数据验证

### 权限控制规范 (RBAC)

- **角色体系**:
  - `admin`: 管理员，拥有所有权限（包括数据清空）。
  - `shangu`: 运营人员，拥有除破坏性操作外的日常操作权限。
- **实现方式**:
  - 后端: `User` 模型 `role` 字段，API 依赖注入 `current_user` 判断权限。
  - 前端: 路由 `meta.roles` 守卫，菜单根据角色动态渲染。

### 数据库规范

- 使用 Alembic 管理所有数据库变更
- 迁移文件必须包含中文注释说明变更原因
- 表名和字段名使用 snake_case

### 代码质量保证

- **语法检查**: 每次修改代码后，必须运行 lint 或 build 命令检查语法错误，杜绝低级语法错误（如多余的括号、未闭合的标签）。
  - 前端: `pnpm --prefix frontend lint` 或 `pnpm --prefix frontend build`
  - 后端: `ruff check`
- **编辑验证**: 使用工具修改文件（如 `replace_file_content`）后，务必检查修改块的上下文，防止引入多余的括号、标签或破坏原有结构。
- **自我修正**: 遇到报错时，优先分析报错信息（如行号、错误类型），定位到具体代码行进行修复，而不是盲目尝试。

---

## 日志分析与问题诊断

### 核心原则

**🔍 问题诊断优先级：日志 > 猜测**

当遇到任何 API 调用失败、数据异常或功能错误时，AI 必须：
1. **第一步：查询日志** - 不要盲目修改代码
2. **第二步：分析数据** - 基于实际数据定位问题
3. **第三步：精准修复** - 针对性解决问题
4. **第四步：验证结果** - 修复后再次检查日志

### 日志系统架构

- **存储位置**: PostgreSQL `system_logs` 表
- **日志分类**:
  - `external_api` - 外部 API 调用（Sorftime, DeepSeek 等）
  - `api_import` - 批量导入业务日志
  - `system` - 系统级日志
- **关键字段**:
  - `level` - 日志级别 (info/error/warning)
  - `category` - 日志分类
  - `message` - 日志消息
  - `context` - JSON 格式的上下文数据
  - `timestamp` - 时间戳

### AI 必须遵循的工作流程

#### 场景 1：API 调用失败

**用户报告**: "抓取失败，提示：未获取到 Best Sellers 数据"

**AI 标准流程**:

```bash
# 1. 查询最近的 API 错误日志
docker exec askjeff-dev-db-1 psql -U sorftime -d askjeff -c "
SELECT 
    to_char(timestamp, 'HH24:MI:SS') as time,
    level,
    message,
    context->>'platform' as platform,
    context->>'status_code' as status,
    context->'response'->>'code' as api_code,
    context->'error_detail' as error
FROM system_logs
WHERE category = 'external_api'
  AND level = 'error'
  AND timestamp >= NOW() - INTERVAL '30 minutes'
ORDER BY timestamp DESC
LIMIT 5;
"

# 2. 如果发现响应解析失败（response 字段为 null），查看原始响应
docker exec askjeff-dev-db-1 psql -U sorftime -d askjeff -c "
SELECT 
    LEFT(context->>'raw_response', 500) as response_preview
FROM system_logs
WHERE category = 'external_api'
  AND level = 'error'
  AND context->'response'->>'code' IS NULL
ORDER BY timestamp DESC
LIMIT 1;
"

# 3. 分析数据，定位问题（如：字段名大小写不匹配）
# 4. 修复代码
# 5. 验证修复：再次查询日志确认 level 变为 info
```

#### 场景 2：数据解析异常

**症状**: API 返回 200，但所有 response 字段都是 null

**诊断步骤**:
1. 查询 `raw_response` 查看实际返回的 JSON
2. 对比 Pydantic 模型定义
3. 检查字段名映射（如 `RequestLeft` vs `requestLeft`）
4. 修复模型配置或添加 `AliasChoices`

#### 场景 3：性能问题

**查询响应时间分布**:

```sql
SELECT 
    context->>'platform' as platform,
    COUNT(*) as calls,
    ROUND(AVG((context->>'duration_ms')::numeric), 0) as avg_ms,
    MAX((context->>'duration_ms')::numeric) as max_ms
FROM system_logs
WHERE category = 'external_api'
  AND timestamp >= NOW() - INTERVAL '1 hour'
GROUP BY context->>'platform';
```

### 常用 SQL 查询模板

#### 1. 快速诊断最近错误

```sql
SELECT 
    to_char(timestamp, 'YYYY-MM-DD HH24:MI:SS') as time,
    message,
    context->>'platform' as platform,
    context->'error_detail' as error,
    LEFT(context->>'raw_response', 200) as response_preview
FROM system_logs
WHERE category = 'external_api'
  AND level = 'error'
  AND timestamp >= NOW() - INTERVAL '30 minutes'
ORDER BY timestamp DESC
LIMIT 5;
```

#### 2. 检查特定平台的调用

```sql
SELECT 
    to_char(timestamp, 'HH24:MI:SS') as time,
    level,
    context->>'status_code' as status,
    context->'response'->>'code' as api_code,
    context->'response'->>'requestLeft' as quota
FROM system_logs
WHERE category = 'external_api'
  AND context->>'platform' = 'Sorftime'
  AND timestamp >= NOW() - INTERVAL '1 hour'
ORDER BY timestamp DESC
LIMIT 10;
```

#### 3. 统计成功率

```sql
SELECT 
    level,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 1) as percentage
FROM system_logs
WHERE category = 'external_api'
  AND timestamp >= NOW() - INTERVAL '1 hour'
GROUP BY level;
```

### 数据库连接信息

- **容器名**: `askjeff-dev-db-1`
- **用户名**: `sorftime`
- **数据库**: `askjeff`
- **查询命令格式**:

  ```bash
  docker exec askjeff-dev-db-1 psql -U sorftime -d askjeff -c "<SQL>"
  ```

### 工作流程文档

详细的日志分析流程和诊断方法，参见：
- [AI 日志分析工作流程](.agent/workflows/ai-log-analysis.md) - AI 专用诊断指南
- [API 问题排查流程](.agent/workflows/troubleshoot-api-issues.md) - 用户/开发者手册

### 最佳实践

**对于 AI**:
- ✅ **问题出现时，第一反应是查日志**
- ✅ **使用精确的时间范围**（用户刚报告的问题查最近 10-30 分钟）
- ✅ **逐步深入**：先看概览统计，再看详情，最后看原始数据
- ✅ **修复后必须验证**：重新查询日志确认问题解决
- ❌ **不要盲目猜测和修改代码**

**对于开发者**:
- ✅ **完善日志记录**：关键节点都要记录，错误时记录完整上下文
- ✅ **使用结构化数据**：context 字段使用 JSON 格式
- ✅ **失败时记录原始响应**：便于调试解析问题

### 日志记录规范

**在代码中记录日志**:

```python
# 成功的 API 调用
LogService.log(
    db,
    level="info",
    category="external_api",
    message="Sorftime API CategoryRequest",
    context={
        "platform": "Sorftime",
        "url": str(response.url),
        "status_code": response.status_code,
        "duration_ms": duration,
        "response": {
            "code": response_data.get("code"),
            "requestLeft": response_data.get("requestLeft"),
            "requestConsumed": response_data.get("requestConsumed")
        }
    }
)

# 失败的 API 调用（额外记录 raw_response）
LogService.log(
    db,
    level="error",
    category="external_api",
    message="Sorftime API CategoryRequest",
    context={
        "platform": "Sorftime",
        "url": str(response.url),
        "status_code": response.status_code,
        "raw_response": response.text[:2000],  # 关键！
        "error_detail": {
            "http_status": response.status_code,
            "api_code": response_data.get("code"),
            "api_message": response_data.get("message")
        }
    }
)
```

---

## 测试策略

### 后端测试
- **单元测试**: 使用 pytest
- **API 测试**: 使用 FastAPI TestClient
- **集成测试**: Mock 外部服务（如 DeepSeek API）
- **数据库测试**: 使用测试数据库（Docker 环境自动配置）
- **运行环境**: 推荐在 Docker 容器中运行测试以确保环境一致性

```bash
# 在 Docker 中运行所有测试
docker exec askjeff-dev-backend-1 poetry run pytest tests/

# 运行特定测试文件
docker exec askjeff-dev-backend-1 poetry run pytest tests/api/test_extraction.py

# 查看测试覆盖率
docker exec askjeff-dev-backend-1 poetry run pytest --cov=app tests/
```

### 前端测试
- ESLint 静态检查
- 中文合规检查
- 类型检查（TypeScript）

---

## 部署

### 开发部署
使用 Docker Compose 热更新模式

### 生产部署
通过 systemd 管理 Docker Compose stack

详见 [README.md](README.md) 的部署章节

---

## 参考资料

- [项目 README](README.md) - 快速启动指南
- [需求管理](specs/README.md) - 所有功能需求索引
- [Spec-Kit 官方文档](https://github.com/github/spec-kit) - 规格驱动开发
- [新需求工作流](.agent/workflows/new-requirement.md) - 创建新需求的步骤
