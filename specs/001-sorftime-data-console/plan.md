# Implementation Plan: Sorftime 数据智能控制台

**Branch**: `001-sorftime-data-console` | **Date**: 2025-11-15 | **Spec**: `specs/001-sorftime-data-console/spec.md`  
**Input**: `/specs/001-sorftime-data-console/spec.md`

## 摘要

- 目标：交付可导入 Sorftime 表格、集中管理批次、支持自然语言问答与可配置导出的运营后台，并输出推荐技术方案。
- 方案：沿用用户指定栈（FastAPI + PostgreSQL + SQLAlchemy + Vue 3 + Vite + Vue Element Admin），去除所有非必要组件。导入/导出通过 FastAPI BackgroundTasks + streaming 实现，文件直接保存在本地挂载目录；问答直接调用 Deepseek API（无 LangChain）并记录引用字段；开发与运维均使用 Docker Compose，生产部署采用 systemd + docker compose（单机或虚拟机），以最少依赖实现需求。
- 交付物：补充《技术选型建议》（`specs/001-sorftime-data-console/tech-selection.md`），涵盖 UI 组件/状态管理/表格图表/后端栈/部署方式及理由，并在 quickstart 提供查阅路径。

## 技术背景

- **语言/版本**：后端 Python 3.12 + FastAPI；前端 Vue 3 + TypeScript；构建工具 Vite 5。
- **核心依赖**：FastAPI、Pydantic v2、SQLAlchemy 2.0、Alembic、HTTPX、FastAPI BackgroundTasks、Deepseek 官方 SDK；前端 Vue Element Admin、Pinia、Vue Router、Axios、ECharts。
- **存储**：PostgreSQL 15（批次、产品、导出日志、QuerySession）、本地挂载目录 `storage/`（上传文件与导出结果）。
- **测试策略**：Pytest + HTTPX（API/快照）、unittest.mock（Deepseek stub）、Playwright（前端端到端）、k6（导入/导出吞吐）、Contract Tests（OpenAPI）。
- **性能验证**：导入 50MB/10 万行 ≤5 分钟（k6/pytest 基准，报告存 `scripts/perf/import-report.md`）；问答 P90 ≤10s（Deepseek 模拟及降级验证，报告存 `scripts/perf/chat-report.md`）；导出 50k+ 行 95% ≤2 分钟（k6，报告存 `scripts/perf/export-report.md`），验证结果需在 quickstart/验收中引用。
- **部署/目标平台**：开发/测试统一使用 Docker Compose（frontend/backend/postgres）。生产为单机 Docker Compose + systemd watcher（或轻量容器主机），无需 K8s；CI 使用 GitHub Actions。
- **性能&约束**：单批次文件≤50MB、10万行；导入 5 分钟内完成；问答 P95 ≤10s；导出 95% 在 2 分钟内完成；界面/文档中文呈现。

## 宪章核对（必须全部满足）

1. **P1 用户意图**：计划保持规格 3 个用户故事 + 技术选型承诺，确保范围明确并在文档/界面中复述。
2. **P2 独立价值**：导入、问答、导出三大模块将独立开发与部署（独立 API、前端路由、测试），任务与验收按故事分组。
3. **P3 合约先行**：Phase 1 输出 OpenAPI（导入/查询/问答/导出），定义数据库 schema 及文件命名规范（存储在 `storage/imports/{batchId}.xlsx`）。
4. **P4 可验证证据**：SC-001~004 映射至 Pytest/k6/Playwright 指标；quickstart 提供手动检查步骤与 SQL 查询（无需大规模监控栈）。
5. **P5 可观测性**：使用 Python logging + JSON formatter 写入文件，并同步写入 PostgreSQL `audit_logs`；提供 `scripts/tail_logs_cn.py` 和 quickstart 指南。
6. **P6 中文交付**：前端默认中文语言包，后端/文档/commit lint 强制中文描述；CI 运行 `scripts/check_cn.py` 避免英文片段。

## 项目结构

### 文档

```text
specs/001-sorftime-data-console/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md   # /speckit.tasks 生成
```

### 代码骨架

```text
frontend/                     # Vue 3 + Vue Element Admin
├── src/
├── tests/

backend/
├── app/
│   ├── api/                  # FastAPI 路由
│   ├── services/             # 导入/问答/导出业务
│   ├── models/               # SQLAlchemy ORM
│   ├── schemas/              # Pydantic
│   └── tasks/                # BackgroundTasks 封装
├── migrations/               # Alembic
├── storage/                  # 本地文件目录（挂载卷）
├── tests/

infra/
└── docker/                   # Compose + systemd 单机部署脚本
```

**结构决策**：仅保留满足需求的最小目录，前后端分离但共享接口契约；后台任务使用 FastAPI BackgroundTasks，无需独立 worker；infra 只包含 Compose 与部署脚本，方便 Dev/Ops。

### 前端基础设施

- 提供主题切换（亮/暗或品牌方案）与基于角色的权限路由/菜单守卫，默认使用中文语言包；文档需说明配置方法与默认示例。

## 复杂度追踪（仅在违反宪章时填写）

| 违反项 | 必要性说明 | 放弃更简单方案的原因 |
|--------|------------|----------------------|
| （暂无） | — | — |
