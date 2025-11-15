from collections.abc import Generator

from sqlalchemy.orm import Session

from app.db import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """FastAPI 依赖 - 注入 SQLAlchemy Session。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
