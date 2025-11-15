# askjeff Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-11-15

## Active Technologies

- **001-sorftime-data-console**
  - 前端：Vue 3 + TypeScript + Vite + Vue Element Admin（Element Plus、Pinia、Vue Router、ECharts）
  - 后端：Python 3.12 + FastAPI、Pydantic v2、SQLAlchemy 2.0、Alembic、HTTPX、FastAPI BackgroundTasks，直接调用 Deepseek API
  - 数据：PostgreSQL 15（批次/产品/日志），本地挂载目录 `backend/storage/` 存放导入与导出文件
  - DevOps：开发 & 生产均采用 Docker Compose（prod 由 systemd 管理 compose stack），日志用 Python logging，指标以脚本导出

## Project Structure

```text
frontend/                # Vue Element Admin
backend/
├── app/                 # FastAPI 应用
├── models/              # SQLAlchemy
├── schemas/             # Pydantic
├── services/            # 业务逻辑
├── tasks/               # BackgroundTasks 封装
└── migrations/          # Alembic
infra/
└── docker/              # Compose 与部署脚本
```

## Commands / Tooling

- `pnpm --prefix frontend lint`：前端 ESLint + 中文校验
- `poetry run ruff check && pytest`：后端静态+单测
- `python scripts/check_cn.py`：全仓中文检查
- `docker compose -f infra/docker/compose.yml up -d`：本地依赖
- `python scripts/report_metrics.py`：生成导入/问答/导出指标 CSV

## Code Style

- 所有代码、注释、Commit 与文档必须使用中文（保留必要术语但需附中文解释）
- Vue 组件使用 `<script setup>` + Composition API；Element Plus 主题需保持中文文案
- FastAPI 模块拆分为 `api/routers`、`services`、`models`；BackgroundTasks 处理导入/导出，无单独 Celery worker

## Recent Changes

- 001-sorftime-data-console：技术栈调整为 FastAPI + PostgreSQL + SQLAlchemy + Vue 3 + Vite + Vue Element Admin

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
