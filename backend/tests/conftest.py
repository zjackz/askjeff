from __future__ import annotations

import os
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.api.deps import get_db
from app.db import Base
from app.main import app

# 确保模型元数据已加载
from app import models as _models  # noqa: F401


def _build_testing_engine() -> tuple[sessionmaker[Session], Engine]:
    """在单测中使用 sqlite，避免依赖外部 PostgreSQL。"""
    tmp_dir = Path(__file__).resolve().parent / ".tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    db_path = tmp_dir / "test.db"
    os.environ.setdefault("STORAGE_DIR", str(Path("backend/storage")))
    engine = create_engine(f"sqlite:///{db_path}", future=True)
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
    """每个用例前后清空 sqlite，避免状态污染。"""
    Base.metadata.drop_all(bind=TestingEngine)
    Base.metadata.create_all(bind=TestingEngine)
    yield
