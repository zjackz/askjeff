# Quickstart - Sorftime 数据智能控制台

> 目标：30 分钟内完成“导入→问答→导出”闭环。全程使用中文界面与日志。

## 1. 准备环境

- Python 3.12、Poetry 1.8、Node.js 20、pnpm 9、Docker Desktop / Colima
- 复制 `.env.example` 至 `.env`，填入 PostgreSQL 连接、Deepseek API Key、应用密钥

## 2. 启动依赖

```bash
docker compose -f infra/docker/compose.yml up -d
poetry install
pnpm install --prefix frontend
```

## 3. 初始化数据库与服务

```bash
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload
pnpm --prefix frontend dev
```

访问：
- 后台入口 `http://localhost:5173`（Vue Element Admin 默认中文主题）
- API 文档 `http://localhost:8000/docs`（FastAPI 自动生成）

## 4. 场景验证

1. **导入**：在“文件导入”上传 `samples/sorftime-demo.xlsx`，选择“追加”策略。观察界面实时状态，确认 5 分钟内批次状态为成功，同时 `backend/storage/imports/` 中生成原始文件与 `{batch_id}_failed.csv`（如有失败行）。
2. **问答**：在“数据洞察”输入“最近两次导入销量最高的 5 个 ASIN”。验证页面展示 Deepseek 答案、引用批次/字段，且 `query_sessions` 表新增记录、`audit_logs` 写入 `chat.ask`。
3. **导出**：筛选同一批次，导出 CSV。下载文件后确认列名中文且 `backend/storage/exports/` 中存在文件，`export_jobs` 状态=成功。

## 5. 观测与日志

- 运行 `python scripts/tail_logs_cn.py`，实时查看中文日志输出。
- 执行 `python scripts/report_metrics.py --days 1`，生成导入耗时、问答延迟、导出成功率报表（CSV）。
- 查询 PostgreSQL `audit_logs` 表，确保包含导入/问答/导出动作。

## 6. 中文合规自检

```bash
pnpm --prefix frontend lint
poetry run ruff check
python scripts/check_cn.py
pytest && pnpm --prefix frontend test
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
