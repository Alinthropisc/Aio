from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine as _create


def create_engine(
    url: str,
    pool_size: int = 10,
    max_overflow: int = 20,
    pool_timeout: int = 30,
    echo: bool = False,
) -> AsyncEngine:
    return _create(
        url,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_timeout=pool_timeout,
        echo=echo,
        pool_pre_ping=True,
        pool_recycle=3600,
    )


@asynccontextmanager
async def lifespan_engine(
    url: str,
    pool_size: int = 10,
    max_overflow: int = 20,
    pool_timeout: int = 30,
    echo: bool = False,
) -> AsyncIterator[AsyncEngine]:
    """Создаёт движок и гарантированно диспозит пул соединений при завершении."""
    engine = create_engine(url, pool_size, max_overflow, pool_timeout, echo)
    try:
        yield engine
    finally:
        await engine.dispose()
