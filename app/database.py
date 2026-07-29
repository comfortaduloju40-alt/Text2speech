"""
Database engine and session management. Single SQLAlchemy engine +
sessionmaker for the whole app. Works with SQLite (local dev) and
PostgreSQL (Railway production) via the same DATABASE_URL-driven engine.
"""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base

from app.config import settings
from app.logger import get_logger

logger = get_logger(__name__)

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Context-manager version for use inside Telegram handlers."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    import app.models  # noqa: F401 — registers models on Base before create_all

    logger.info("Initializing database (create_all)...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database ready.")
