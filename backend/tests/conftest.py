from __future__ import annotations

import os
from pathlib import Path

# ⚠️ 必须在导入 app 模块之前设置测试环境变量
os.environ.setdefault("TESTING", "1")
os.environ.setdefault("STORAGE_DIR", str(Path("backend/storage")))
os.environ.setdefault("SECRET_KEY", "test_secret_key_for_testing_only")
os.environ.setdefault("DEEPSEEK_API_KEY", "test_deepseek_key_for_testing")
os.environ.setdefault("SORFTIME_API_KEY", "test_sorftime_key_for_testing")

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import Session, sessionmaker

from app.api.deps import get_db
from app.db import Base
from app.main import app

# 确保模型元数据已加载
from app import models as _models  # noqa: F401


def _build_testing_engine() -> tuple[sessionmaker[Session], Engine]:
    """测试统一使用 PostgreSQL `_dev` 库，符合 Speckit 合约先行要求。"""
    url = os.environ.get(
        "TEST_DATABASE_URL",
        os.environ.get(
            "DATABASE_URL",
            "postgresql+psycopg://sorftime:sorftime@localhost:5432/sorftime_dev",
        ),
    )
    db_url = make_url(url)

    # 确保测试数据库存在（需要 sorftime 具备创建权限）
    admin_url = db_url.set(database="postgres")
    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT", future=True)
    with admin_engine.connect() as conn:
        exists = conn.execute(text("SELECT 1 FROM pg_database WHERE datname=:db"), {"db": db_url.database}).scalar()
        if not exists:
            conn.execute(text(f"CREATE DATABASE {db_url.database} OWNER {db_url.username}"))

    engine = create_engine(db_url, pool_pre_ping=True, future=True)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    return session_factory, engine


TestingSessionLocal, TestingEngine = _build_testing_engine()


def override_get_db() -> Session:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def _reset_db() -> None:
    """每个用例前后清空 PostgreSQL `_dev`，避免状态污染。"""
    keep_after = os.getenv("TEST_KEEP_DB", "").lower() in {"1", "true", "yes"}
    Base.metadata.drop_all(bind=TestingEngine)
    Base.metadata.create_all(bind=TestingEngine)
    yield
    if not keep_after:
        Base.metadata.drop_all(bind=TestingEngine)
        Base.metadata.create_all(bind=TestingEngine)


@pytest.fixture
def db() -> Session:
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
