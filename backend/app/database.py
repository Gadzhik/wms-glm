"""Database setup and session management for SQLAlchemy async"""
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import StaticPool

from app.config import settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models"""
    pass


# Global variables for database engine and session factory
_engine = None
_AsyncSessionLocal = None


def get_engine():
    """Get or create database engine"""
    global _engine, _AsyncSessionLocal
    if _engine is None:
        _engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
            future=True,
            poolclass=StaticPool if "sqlite" in settings.DATABASE_URL else None,
            connect_args={
                "check_same_thread": False,
            } if "sqlite" in settings.DATABASE_URL else {},
        )
        _AsyncSessionLocal = async_sessionmaker(
            _engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    return _engine


def get_session_factory():
    """Get async session factory"""
    return _AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database session.
    
    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    """
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for getting async database session.
    
    Usage:
        async with get_db_context() as db:
            result = await db.execute(select(Item))
            items = result.scalars().all()
    """
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database - create tables if they don't exist"""
    from sqlalchemy import text
    engine = get_engine()
    
    # Ensure data directory exists
    db_path = Path(settings.database_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Enable SQLite optimizations
    if "sqlite" in settings.DATABASE_URL:
        async with engine.begin() as conn:
            await conn.execute(text("PRAGMA journal_mode=WAL"))
            await conn.execute(text("PRAGMA synchronous=NORMAL"))
            await conn.execute(text("PRAGMA cache_size=-64000"))
            await conn.execute(text("PRAGMA foreign_keys=ON"))
            await conn.execute(text("PRAGMA temp_store=MEMORY"))


async def close_db() -> None:
    """Close database connections"""
    global _engine
    if _engine:
        await _engine.dispose()


async def check_db_connection() -> bool:
    """Check if database connection is healthy"""
    from sqlalchemy import text
    try:
        session_factory = get_session_factory()
        async with session_factory() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"Database connection check failed: {e}")
        return False


async def vacuum_db() -> None:
    """Run VACUUM on SQLite database to reclaim space"""
    if "sqlite" not in settings.DATABASE_URL:
        return
    
    global _engine, _AsyncSessionLocal
    
    # Close all connections before VACUUM
    if _engine:
        await _engine.dispose()
    
    # Create new engine without StaticPool for VACUUM
    vacuum_engine = create_async_engine(
        settings.DATABASE_URL.replace("sqlite+aiosqlite", "sqlite"),
        echo=False,
        connect_args={"check_same_thread": False},
    )
    
    try:
        async with vacuum_engine.begin() as conn:
            await conn.execute("VACUUM")
            await conn.execute("ANALYZE")
    finally:
        await vacuum_engine.dispose()
        # Recreate original engine
        _engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
            future=True,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
        )
        _AsyncSessionLocal = async_sessionmaker(
            _engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
