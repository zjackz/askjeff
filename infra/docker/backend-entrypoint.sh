#!/usr/bin/env bash
set -euo pipefail

# 等待数据库可用（通过 SQLAlchemy 连接测试）
poetry run python - <<'PY'
import os, time
from sqlalchemy import create_engine, text

url = os.environ.get('DATABASE_URL')
if not url:
    raise SystemExit('DATABASE_URL 未设置')

for i in range(60):
    try:
        engine = create_engine(url, future=True)
        with engine.connect() as conn:
            conn.execute(text('SELECT 1'))
        print('Database is ready')
        break
    except Exception as e:  # noqa: BLE001
        print('Waiting for database...', e)
        time.sleep(2)
else:
    raise SystemExit('数据库连接超时')
PY

# 运行 Alembic 迁移
poetry run alembic upgrade head

# 自动创建默认用户（如果脚本存在）
if [ -f "scripts/init_admin.py" ]; then
    echo "Initializing admin users..."
    poetry run python scripts/init_admin.py || echo "Admin initialization skipped or failed."
fi

# 启动 Uvicorn
PORT=${BACKEND_PORT:-8000}
echo "Starting backend on port $PORT..."
exec poetry run uvicorn app.main:app --host 0.0.0.0 --port "$PORT"

