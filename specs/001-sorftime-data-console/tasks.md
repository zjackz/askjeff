# Tasks: Sorftime 数据智能控制台

**输入**：`/specs/001-sorftime-data-console/` 内的 plan/spec/research/data-model/contracts  
**前置**：plan.md、spec.md 必须完成  
**语言合规**：代码、注释、提交记录、任务描述、交付文档均需中文呈现，英文术语需附中文注解。

> 任务按用户故事分组，确保每个故事可独立交付。若存在跨故事依赖，需说明原因。

## 任务格式

`[ID] [P?] [US#] 描述（含文件路径）`

- `[P]` 表示可并行（无共享文件/依赖）
- `[US#]` 对应用户故事编号
- 每个故事至少包含：实现任务、验证任务（测试或验收清单）、可观测性/文档任务

## 阶段 1：基础环境

- [x] T001 初始化 `frontend/` 与 `backend/` 目录结构及 pnpm/poetry 配置
- [x] T002 配置 Docker Compose（`infra/docker/compose.yml`）含 FastAPI、PostgreSQL、Vite 前端
- [x] T003 [P] 建立 GitHub Actions 流水线模板（`.github/workflows/ci.yml`）运行 lint/test/中文检查
- [x] T004 [P] 配置 Ruff + ESLint + `scripts/check_cn.py` 并在 `package.json`/`pyproject.toml` 中添加命令

## 阶段 2：通用基础能力

- [x] T005 创建 SQLAlchemy Base、数据库连接及 Alembic 配置（`backend/app/db.py`,`backend/migrations/`）
- [x] T006 实现通用 Pydantic 响应模型与异常处理（`backend/app/api/deps.py`、`backend/app/api/errors.py`）
- [x] T007 [P] 建立全局审计日志表与写入工具（`backend/app/services/audit_service.py`）
- [x] T008 [P] 在前端接入 Vue Element Admin 基础布局、登录占位页（`frontend/src/`）
- [x] T009 [P] 设置后端与前端的中文文案/提示枚举，确保默认语言为中文
- [x] T0DB 统一测试使用 PostgreSQL `sorftime_dev`，移除 SQLite 依赖，测试前自动迁移到 `_dev` 库
- [ ] T0YC [P] 实现主题切换（亮/暗或品牌主题），提供配置说明与至少一条组件/截图验证（`frontend/src/styles/theme/`）
- [ ] T0YD 基于角色的权限路由/菜单守卫，示例角色配置写入 quickstart（`frontend/src/router/`）
- [ ] T0YE [P] Playwright/组件测试覆盖主题切换与权限守卫可用性（`frontend/tests/`）

## 阶段 3：User Story 1 - Sorftime 批次导入 (Priority: P1) 🎯

- **目标**：实现 CSV/XLSX 上传、字段校验、批次状态跟踪及失败行导出。
- **独立验证**：上传样例文件后查看批次列表与失败行，验证状态/统计准确且日志记录完整。

### Tests / Evidence

- [x] T010 [US1] 编写导入接口 Pytest + HTTPX 用例（`backend/tests/api/test_imports.py`），覆盖成功/失败行
- [x] T011 [P][US1] 编写 Playwright 脚本验证上传流程（`frontend/tests/e2e/import.spec.ts`）
- [ ] T0XZ [US1] 导入性能基准：50MB/10 万行 k6/pytest，记录耗时/失败率，输出 `scripts/perf/import-report.md`

### Implementation

- [x] T012 [US1] 建立 `import_batches`、`product_records` ORM + CRUD（`backend/app/models/import_batch.py`,`backend/app/models/product_record.py`）
- [x] T013 [US1] 实现 Sorftime 文件解析与校验服务（`backend/app/services/import_service.py`）
- [x] T014 [US1] 在 FastAPI 中创建上传/批次列表/详情 API（`backend/app/api/routes/imports.py`）
- [x] T015 [P][US1] 前端实现“文件导入”页面：上传组件、策略选择、进度与失败行展示（`frontend/src/views/import/index.vue`）
- [x] T016 [US1] 将原始文件与失败行 CSV 写入 `backend/storage/imports/` 并记录路径

### Observability / Docs

- [x] T017 [US1] 编写导入日志输出（JSON）及 audit 记录（`backend/app/services/audit_service.py`）
- [x] T018 [US1] 在 quickstart 中补充导入操作步骤与失败行导出说明（`specs/001-sorftime-data-console/quickstart.md`）

## 阶段 4：User Story 2 - 自然语言数据洞察 (Priority: P2)

- **目标**：提供 Deepseek 问答入口，基于本地数据生成中文答案并列出引用字段。
- **独立验证**：构造 3 条典型问题，确认回答含引用批次/字段，断网或 API 失败时给出替代提示。

### Tests / Evidence

- [x] T019 [US2] 为问答 API 编写 Pytest 用例（含 Deepseek mock），校验成功与失败路径（`backend/tests/api/test_chat.py`）
- [x] T020 [P][US2] 前端编写组件单测/快照（`frontend/tests/components/chat.spec.ts`）
- [ ] T0YA [US2] 问答性能与降级验证：P90 ≤10s，Deepseek 失败时降级路径可用，输出 `scripts/perf/chat-report.md`

### Implementation

- [x] T021 [US2] 创建 `query_sessions` ORM + Service（`backend/app/models/query_session.py`,`backend/app/services/chat_service.py`）
- [x] T022 [US2] 编写 SQL 聚合模板与 Deepseek 请求封装（`backend/app/services/deepseek_client.py`）
- [x] T023 [US2] 新增问答 API（`backend/app/api/routes/chat.py`），处理失败降级逻辑
- [x] T024 [P][US2] 实现前端问答界面：输入框、历史记录、引用字段表格（`frontend/src/views/chat/index.vue`）

### Observability / Docs

- [x] T025 [US2] 将问答请求/响应写入 `query_sessions` 与审计日志，含中文上下文（`backend/app/services/chat_service.py`）
- [x] T026 [US2] 在 quickstart 中增加问答验证脚本与 Deepseek 配置说明（`specs/001-sorftime-data-console/quickstart.md`）

## 阶段 5：User Story 3 - 数据导出与稽核 (Priority: P3)

- **目标**：按筛选条件导出 CSV/XLSX、记录导出日志并可下载失败行。
- **独立验证**：设置条件导出后，2 分钟内收到文件，日志记录筛选条件与操作者，失败任务可重试。

### Tests / Evidence

- [x] T027 [US3] 为导出 API 编写 Pytest（成功/失败/重试）（`backend/tests/api/test_exports.py`）
- [x] T028 [P][US3] 前端编写导出流程 e2e 测试（`frontend/tests/e2e/export.spec.ts`）
- [ ] T0YB [US3] 导出性能与分段测试：50k+ 行 95% ≤2 分钟，支持失败重试，输出 `scripts/perf/export-report.md`

### Implementation

- [x] T029 [US3] 创建 `export_jobs` ORM + Service，保存条件/字段/文件路径（`backend/app/models/export_job.py`,`backend/app/services/export_service.py`）
- [x] T030 [US3] 在 FastAPI 中实现创建导出/查询状态/下载接口（`backend/app/api/routes/exports.py`）
- [x] T031 [US3] 前端实现导出配置表单与任务列表（`frontend/src/views/export/index.vue`）
- [x] T032 [US3] 生成 CSV/XLSX 并保存在 `backend/storage/exports/`，失败时支持重试

### Observability / Docs

- [x] T033 [US3] 记录导出日志到 `audit_logs` 并提供失败行下载链接
- [x] T034 [US3] 更新 quickstart 的导出与日志核查步骤（`specs/001-sorftime-data-console/quickstart.md`）
- [ ] T0XX [P][US3] 撰写《技术选型建议》文档（UI 组件、状态管理、表格/图表、后端栈、部署方式与理由），存放 `specs/001-sorftime-data-console/tech-selection.md`
- [ ] T0XY [US3] 审阅技术选型文档并在 quickstart 增加查阅步骤，确认文档存在且理由完整

## 阶段 N：收尾与跨故事事项

- [x] T035 编写 `scripts/report_metrics.py`，从数据库统计导入/问答/导出指标并输出 CSV
- [x] T036 [P] 在 README 或运维手册中记录 Docker Compose + systemd 部署方式
- [x] T037 完成文档/界面中文审查，运行 `scripts/check_cn.py` 并修复所有警告
- [x] T038 [P] Playwright 全流程脚本：导入 → 问答 → 导出，提供演示截图

## Dependencies & Execution Order

- User Story 1 完成后才能提供可靠数据供 US2/US3 查询与导出（US1 → US2/US3 并行）
- US2/US3 可在 US1 数据结构稳定后并行推进
- 快观测/quickstart 更新在各故事完成时立即执行，避免遗漏

## Parallel Example

```bash
# US1 并行任务
Task T012 + T013 (后端模型/服务) 可与 T015 (前端页面) 并行

# US2 并行任务
Task T021 (模型) 与 T024 (前端) 可同时进行；Deepseek Mock 测试 T019 需在 API 完成前先写好
```

## Implementation Strategy

1. 完成阶段 1+2，搭好基础与数据库迁移。
2. 先实现 US1 形成可导入/查看数据的 MVP（建议首个发布）。
3. US1 验收后并行推进 US2、US3，保持各自独立验证。
4. 最后执行收尾任务（指标脚本、部署文档、语言检查）。
