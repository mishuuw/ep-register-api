from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import AsyncAdaptedQueuePool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from src.config.settings import get_database_settings

engine = create_async_engine(
    get_database_settings().async_url,
    poolclass=AsyncAdaptedQueuePool,
    pool_size=300,
    max_overflow=100,
    pool_recycle=3600,
    pool_timeout=30,
    query_cache_size=500,
)

session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    session = session_maker()
    async with session.begin():
        yield session
    await session.close()


async def get_session_obj() -> AsyncGenerator[AsyncSession, None]:
    session = session_maker()
    async with session.begin():
        yield session
    await session.close()


async def shutdown() -> None:
    if engine is not None:
        await engine.dispose()
