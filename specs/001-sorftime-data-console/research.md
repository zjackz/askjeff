# Research - Sorftime 数据智能控制台

> 所有结论基于“FastAPI + PostgreSQL + SQLAlchemy + Vue 3 + Vite + Vue Element Admin”的硬性约束，补充必要的组件以满足需求。

## 决策 1：后端框架与结构
- **Decision**: FastAPI + Python 3.12，使用 Pydantic v2、SQLAlchemy 2.0 ORM、Alembic 管理迁移，服务层依赖注入。
- **Rationale**: 符合用户指定栈；FastAPI 异步能力可支撑导入/问答并发；Pydantic 生成 OpenAPI，有助于宪章 P3；SQLAlchemy 2.0 原生类型注解便于维护。
- **Alternatives considered**: 保守同步写法（Flask）但缺少自动文档与性能；Django ORM 违背技术栈要求。

## 决策 2：导入/导出执行方式
- **Decision**: 不引入消息队列，直接使用 FastAPI `BackgroundTasks` 执行导入解析与导出生成；原始文件与导出结果保存在 `backend/storage/`（Docker 卷或主机目录），数据库记录路径。
- **Rationale**: 文件规模 ≤50MB，可在单机上于 5 分钟内完成；BackgroundTasks 简单可控，避免 Celery/Redis 维护；本地存储无需额外对象服务。
- **Alternatives considered**: Celery + Redis（额外运维成本）；MinIO/S3（对当前规模过重）。

## 决策 3：前端框架与组件
- **Decision**: Vue 3 + Vite + Vue Element Admin（基于 Element Plus + Vue Router + Pinia）；表格/图表沿用 Element Plus Table + ECharts。
- **Rationale**: 满足用户指定栈；Vue Element Admin 内置权限路由/主题/导航骨架；Pinia 简化状态管理；Vite 提升开发速度；Element Plus 拥有丰富的中后台控件。
- **Alternatives considered**: 其它 admin 模板（Naive Admin、Arco Admin）但不在要求列表。

## 决策 4：自然语言问答实现
- **Decision**: 直接调用 Deepseek API（官方 Python SDK），使用自定义 Prompt 模板引导模型依据我们提供的 SQL 汇总结果给出中文答案；SQL 查询逻辑由后端手写（Query Builder），同时返回引用批次/字段。
- **Rationale**: 摆脱 LangChain 依赖，调试简单；SQL 控制权在后端，可确保结果可追溯；仍满足“类似 ChatGPT”体验。
- **Alternatives considered**: LangChain（增加复杂度）、自研向量检索（超出范围）。

## 决策 5：DevOps 与可观测性
- **Decision**: Dev 与 Prod 均使用 Docker Compose（Prod 通过 systemd 自动拉起）；日志采用 Python logging + Vue 前端 console 上传，统一写入文件并定期归档；指标以简单 SQL 统计 + `scripts/report_metrics.py`（输出 CSV）形式呈现。
- **Rationale**: 无需维护 K8s/GitOps/Prometheus/Loki 等重型组件；单机 Compose 易于运维；脚本方式即可满足当前指标需求。
- **Alternatives considered**: K3s + Argo + OTel（超出最小可用范围）；SaaS 监控（需网络与预算）。

## 决策 6：中文合规工具链
- **Decision**: 保留 `scripts/check_cn.py` + ESLint + Ruff 检查，CI（GitHub Actions）运行 `pnpm lint`、`poetry run ruff check`、`python scripts/check_cn.py`；额外提供 pre-commit 钩子方便开发者本地执行。
- **Rationale**: 自动检测即可满足宪章 P6，无需外部服务。
- **Alternatives considered**: 纯人工校对或沉重 i18n 平台。
