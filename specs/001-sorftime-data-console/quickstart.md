# Quickstart - Sorftime 数据智能控制台

> 目标：30 分钟内完成“导入→问答→导出”闭环。全程使用中文界面与日志；所有命令默认在 Docker Compose 容器内执行。

## 1. 准备环境

- Python 3.12、Poetry 1.8、Node.js 20、pnpm 9、Docker Desktop / Colima（`docker compose version` ≥ 2.20）
- 复制 `.env.example` 至 `.env`，填入 PostgreSQL 连接、Deepseek API Key、应用密钥
- 导入映射：如需自定义列别名/必填规则，将 `backend/config/import_mapping.example.yaml` 复制为同目录下的 `import_mapping.yaml` 后修改

## 2. 启动依赖

```bash
# 默认 dev 环境（8001/5174，数据库 sorftime_dev）
make up
# 测试环境：COMPOSE_ENV=test make up  (# 8000/5173，数据库 sorftime_test)

# 在容器内安装依赖
docker compose -f infra/docker/compose.yml run --rm backend poetry install
docker compose -f infra/docker/compose.yml run --rm frontend pnpm install
```

## 3. 初始化数据库与服务

```bash
docker compose -f infra/docker/compose.yml run --rm backend poetry run alembic upgrade head
docker compose -f infra/docker/compose.yml up backend frontend
```

访问：
- 后台入口 `http://localhost:5173`（Vue Element Admin 默认中文主题）
- API 文档 `http://localhost:8000/docs`（FastAPI 自动生成）

## 4. 场景验证

1. **导入**：在“文件导入”上传 `samples/sorftime-demo.xlsx`，选择“追加”策略。观察界面实时状态，确认 5 分钟内批次状态为成功，同时 `backend/storage/imports/` 中生成原始文件与 `{batch_id}_failed.csv`（如有失败行）。验证 Sorftime 字段变更提示与映射（缺列提示、下载最新模板）。
2. **问答**：在“数据洞察”输入“最近两次导入销量最高的 5 个 ASIN”。验证页面展示 Deepseek 答案、引用批次/字段，且 `query_sessions` 表新增记录、`audit_logs` 写入 `chat.ask`。再模拟 Deepseek API 失败（断开网络或使用故障密钥），确认界面提供结构化筛选降级提示。
3. **导出**：筛选同一批次，导出 CSV。下载文件后确认列名中文且 `backend/storage/exports/` 中存在文件，`export_jobs` 状态=成功。对 50k+ 行条件执行分段导出，验证超时/进度提示与失败重试。

### 导入字段规则提示

- 默认仅解析 sheet “产品详情”，可在上传时选择其他 sheet；缺失则导入直接报错。
- 最小必填：`asin`、`title`、`currency`。缺失时行标记 error，写入失败行文件，不入库。
- 列别名示例：`价格|售价|Price -> price`，`币种|Currency -> currency`，`产品标题|Title -> title`，`类目|Category -> category`，`销量排名|SalesRank -> sales_rank`。未知列保留在 `raw_payload`。
- 类型/枚举/单位转换：数值统一为两位小数；日期转 UTC；币种使用白名单，失败记 warning 并保留原值。
- 失败行文件路径：`backend/storage/exports/failed/{batch_id}.csv`，包含行号、原因、原始行 JSON；列覆盖率与警告计数写在批次 `failure_summary`。

## 5. 观测与日志

- 运行 `docker compose -f infra/docker/compose.yml run --rm backend python scripts/tail_logs_cn.py`，实时查看中文日志输出。
- 执行 `docker compose -f infra/docker/compose.yml run --rm backend python scripts/report_metrics.py --days 1`，生成导入耗时、问答延迟、导出成功率报表（CSV）。
- 查询 PostgreSQL `audit_logs` 表，确保包含导入/问答/导出动作。
- 日志中心：前端菜单“日志中心”可按级别/分类/关键字查看系统日志，支持一键 AI 诊断。
- 后端日志 API：
  - `GET /logs`：分页筛选 level/category/keyword/time。
  - `GET /logs/{id}`：日志详情。
  - `POST /logs/analyze`：对指定 logIds 或筛选结果做启发式/AI 诊断。
- 迁移：新增 `system_logs` 表，需执行 `poetry run alembic upgrade head`（或容器内同名命令）后方可使用。

## 6. 中文合规自检

```bash
docker compose -f infra/docker/compose.yml run --rm frontend pnpm lint
docker compose -f infra/docker/compose.yml run --rm backend poetry run ruff check
docker compose -f infra/docker/compose.yml run --rm backend python scripts/check_cn.py
docker compose -f infra/docker/compose.yml run --rm backend pytest
docker compose -f infra/docker/compose.yml run --rm frontend pnpm test
# 前端 E2E（容器内，报告在 frontend/playwright-report）
make test-frontend-e2e
```

CI 会复用上述命令。若出现英文词条需在 PR 中注明原因或修复。

## 7. 测试数据库（PostgreSQL）

- 测试与本地验证统一使用 PostgreSQL `_dev` 库，禁止 SQLite。
- 初始化（需容器已启动，默认凭证 sorftime/sorftime）：

```bash
psql "postgresql://sorftime:sorftime@localhost:5432/postgres" -tc "SELECT 1 FROM pg_database WHERE datname='sorftime_dev'" | grep -q 1 || \
  psql "postgresql://sorftime:sorftime@localhost:5432/postgres" -c "CREATE DATABASE sorftime_dev OWNER sorftime"
DATABASE_URL=postgresql+psycopg://sorftime:sorftime@localhost:5432/sorftime_dev poetry run alembic upgrade head
```

- 若宿主机未安装 psql，可使用容器执行（默认 compose 服务名为 db）：  
  `docker exec docker-db-1 psql -U sorftime -d postgres -c "CREATE DATABASE sorftime_dev OWNER sorftime"`

- 运行后端测试时指定：

```bash
TEST_DATABASE_URL=postgresql+psycopg://sorftime:sorftime@localhost:5432/sorftime_dev poetry run pytest
```

## 8. 满意度调研（SC-004）

- 选取 ≥10 位运营/选品用户，使用上述流程体验导入→问答→导出。
- 使用统一问卷记录满意度（1-5 分），计算总体满意度 = 满意/非常满意占比，门槛 ≥80%。
- 将结果与改进项写入 `scripts/perf/chat-report.md` 或单独调研记录；若低于门槛，列出补救计划。
