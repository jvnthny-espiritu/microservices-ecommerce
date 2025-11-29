import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.pool import QueuePool

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./user.db")


def _get_int_env(key: str, default: int) -> int:
    """Get integer value from environment variable with validation."""
    value = os.getenv(key, str(default))
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"Invalid integer value for {key}: '{value}'")


# Connection pool settings for high traffic (configurable via env vars)
POOL_SIZE = _get_int_env("DB_POOL_SIZE", 5)
MAX_OVERFLOW = _get_int_env("DB_MAX_OVERFLOW", 10)
POOL_TIMEOUT = _get_int_env("DB_POOL_TIMEOUT", 30)
POOL_RECYCLE = _get_int_env("DB_POOL_RECYCLE", 1800)  # Recycle connections after 30 min

connect_args = {}
pool_class = QueuePool

if DATABASE_URL.startswith("sqlite"):
    # SQLite doesn't support connection pooling the same way
    connect_args = {"check_same_thread": False}
    pool_class = None  # Use default StaticPool for SQLite

engine_kwargs = {
    "connect_args": connect_args,
    "future": True,
}

# Only apply pooling for non-SQLite databases
if pool_class:
    engine_kwargs.update({
        "poolclass": pool_class,
        "pool_size": POOL_SIZE,
        "max_overflow": MAX_OVERFLOW,
        "pool_timeout": POOL_TIMEOUT,
        "pool_recycle": POOL_RECYCLE,
        "pool_pre_ping": True,  # Verify connections before use
    })

engine = create_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Yield a DB session and ensure it is closed after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
