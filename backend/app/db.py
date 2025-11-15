import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


def _get_database_url() -> str:
    default = "postgresql+psycopg://sorftime:sorftime@localhost:5432/sorftime"
    return os.getenv("DATABASE_URL", default)


DATABASE_URL = _get_database_url()


class Base(DeclarativeBase):
    """SQLAlchemy Declarative Base"""


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db_session() -> Generator:
    """Manual session scope (FastAPI 依赖在 deps 中封装)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
