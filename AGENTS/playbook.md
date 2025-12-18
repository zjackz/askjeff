# 项目开发手册（可复制模板）

> 约束：如与 `AGENTS.md` 冲突，以 `AGENTS.md` 为准。
> 使用方式：复制到新项目后，按本项目实际情况替换“技术栈、容器名、命令与目录”等占位信息。

## 0. 项目占位符（复制后必须替换）

- 本项目建议统一通过 `Makefile` 执行容器命令（见第 4 节），避免手写容器名与 Compose 参数

## 1. 技术栈速览（按项目替换）

- 前端：Vue 3 + TypeScript + Vite；Element Plus（Vue Element Admin）；Pinia；Vue Router；ECharts；pnpm
- 后端：FastAPI（Python 3.12+）；Pydantic v2；SQLAlchemy 2；Alembic；HTTPX；BackgroundTasks
- 数据：PostgreSQL 15；文件存储 `backend/storage/`
- DevOps：Docker + Docker Compose；生产通过 systemd 管理 Compose stack

## 2. 开发流程（需求 → 实施 → 验证 → 推送）

### 2.1 新需求

- 需求管理入口：`specs/README.md`
- 创建新需求：在 AI 助手中执行 `/new-requirement`
- 产物：`specs/00X-*/spec.md`、`plan.md`、`tasks.md`，并注册到 `specs/README.md`

### 2.2 分支策略

- 主分支：`main`（默认都在此开发）
- 临时分支：仅用于大型重构/实验，完成后合并删除
- 备份分支：`backup/*`

### 2.3 提交信息（必须中文）

- `feat(编号): 描述` / `fix(编号): 描述` / `docs: 描述` / `test: 描述` / `refactor: 描述` / `chore: 描述`

## 3. 验证门禁（交付前必须）

### 3.1 前端

```bash
pnpm --prefix frontend lint
```

### 3.2 后端（优先 Docker；避免环境差异）

```bash
make test-backend
```

### 3.3 中文合规检查

```bash
python3 scripts/check_cn.py
```

### 3.4 测试覆盖底线

- 新增 API 端点：必须有对应集成测试
- 核心 Service：必须有单元测试
- 复杂数据处理：必须有测试用例

## 4. 常用命令

### 4.1 Docker Compose（开发环境）

```bash
make up
make ps
make down
make backend-logs
make frontend-logs
```

也可直接：

```bash
docker compose -f infra/docker/compose.dev.yml up -d
```

## 5. UI 规范（项目覆盖规则）

> 说明：通用 UI/UX 规范见 `AGENTS/ui-ux-guidelines.md`；本节是“本项目额外强制约束”。

- 全局尺寸：Element Plus 使用默认尺寸（`size="default"`）；禁止随意 `size="small"`
  - 例外：表格行内极紧凑操作（需说明原因）
- 表格布局：使用全屏 Flex，表格高度自适应（`height="100%"`），避免页面滚动条
- 表格容器：包裹在 `.table-container`，并使用统一圆角与阴影
- 分页：必须提供 `page-sizes` `[20, 50, 100, 200]`，默认每页 50 条

## 6. 权限控制（RBAC）

- 角色：
  - `admin`：管理员，拥有所有权限（含破坏性操作）
  - `shangu`：运营人员，拥有日常操作权限（不含破坏性操作）
- 后端：`User.role` + `current_user` 依赖注入判断权限
- 前端：路由 `meta.roles` 守卫；菜单按角色动态渲染

## 7. 日志排障（先查日志再改代码）

### 7.1 数据库连接

- 容器：`<db-container>`
- 用户：`<db-user>`
- 库：`<db-name>`

```bash
docker exec <db-container> psql -U <db-user> -d <db-name> -c "<SQL>"
```

### 7.2 快速查看最近 API 错误

- 优先使用脚本：`quick_check_api_logs.sh`
- 或按工作流排查：`.agent/workflows/ai-log-analysis.md` 与 `.agent/workflows/troubleshoot-api-issues.md`

### 7.3 进一步工作流

- AI 日志分析流程：`.agent/workflows/ai-log-analysis.md`
- API 问题排查流程：`.agent/workflows/troubleshoot-api-issues.md`
