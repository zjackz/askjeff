FROM python:3.12-slim

# 固化 Python 工具与虚拟环境位置，避免因工作目录挂载而丢失依赖
ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=2.2.1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
    POETRY_HTTP_TIMEOUT=120

WORKDIR /app

# 安装 Poetry（使用官方推荐的 pip 安装方式）
RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}"

# 先复制依赖声明并安装依赖（不安装本项目本身）
COPY backend/pyproject.toml backend/poetry.lock ./
RUN poetry install --only main --no-interaction --no-ansi --no-root

# 再复制应用源码
COPY backend/ /app/

# 入口脚本负责等待数据库、执行迁移并启动服务
COPY infra/docker/backend-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV PYTHONPATH=/app \
    STORAGE_DIR=/app/storage

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
