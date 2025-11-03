"""
db.py
------
Asynchronous database engine and session management for the FastAPI service.

Implements SQLAlchemy 2.0 async engine setup, connection pooling, and
graceful initialization and shutdown routines.

✅ Uses `sqlite+aiosqlite` for local development.
✅ Provides `get_session()` dependency for FastAPI routes.
✅ Logs all lifecycle events through the global structured logger.
✅ Matches the fail-fast, leave-a-trail, and graceful-shutdown philosophy.

"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings
from app.core.logging import log


# ---------------------------------------------------------------------------
# Database Configuration
# ---------------------------------------------------------------------------

DATABASE_URL = "sqlite+aiosqlite:///./app.db"
"""Default SQLite connection URL for async SQLAlchemy engine."""


class Base(DeclarativeBase):
    """
    Declarative base class for ORM models.

    All ORM entities must inherit from this base to ensure metadata is
    properly registered for table creation and schema synchronization.
    """
    pass


# ---------------------------------------------------------------------------
# Engine and Session Configuration
# ---------------------------------------------------------------------------

engine = create_async_engine(
    DATABASE_URL,
    echo=False,           # Disable SQL echo in logs (set True for debugging)
    echo_pool=True,       # Log pool checkout/return events for diagnostics
    pool_size=5,          # Maintain up to 5 concurrent connections
    max_overflow=10,      # Allow overflow connections during peak load
    pool_timeout=30,      # Timeout (seconds) for acquiring a connection
    pool_recycle=1800,    # Recycle connections after 30 minutes
    future=True,          # Enable SQLAlchemy 2.0 style API
)


SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)
"""Async session factory for use in route dependencies."""


# ---------------------------------------------------------------------------
# Dependency and Lifecycle Methods
# ---------------------------------------------------------------------------

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields a managed async database session.

    Yields:
        AsyncSession:
            Active SQLAlchemy asynchronous session for database operations.

    Example:
        ```python
        @router.get("/items")
        async def list_items(db: AsyncSession = Depends(get_session)):
            ...
        ```
    """
    async with SessionLocal() as session:
        yield session


async def init_db() -> None:
    """
    Initialize database connection and create all tables.

    Runs schema creation for all registered ORM models within the defined
    declarative base. Should be called once at application startup.

    Raises:
        Exception:
            If table creation or engine initialization fails.
    """
    from app.models.db_models import ItemORM  # Ensure model import triggers metadata registration

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        log.info("Database initialized", url=str(engine.url), service=settings.app_name)

    except Exception as e:
        log.error("Database initialization failed", error=str(e))
        raise


async def close_db() -> None:
    """
    Close and dispose of all database engine connections.

    Should be called during application shutdown to ensure all pooled
    connections are properly released and resources are freed.
    """
    await engine.dispose()
    log.info("Database connection closed", service=settings.app_name)
