from collections.abc import AsyncIterator
from typing import Annotated

from dishka import Provider, Scope, provide, from_context
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from config import DatabaseSettings, SecondaryDatabaseSettings
from core.db import create_engine, get_session, session_factory


# Именованные типы чтобы Dishka различала два движка
PrimaryEngine = Annotated[AsyncEngine, "primary"]
SecondaryEngine = Annotated[AsyncEngine, "secondary"]
PrimarySessionFactory = Annotated[async_sessionmaker[AsyncSession], "primary"]
SecondarySessionFactory = Annotated[async_sessionmaker[AsyncSession], "secondary"]
PrimarySession = Annotated[AsyncSession, "primary"]
SecondarySession = Annotated[AsyncSession, "secondary"]


class DatabaseProvider(Provider):
    # ── Primary (PostgreSQL) ───────────────────────────────────────────────────
    @provide(scope=Scope.APP)
    def get_primary_engine(self, settings: DatabaseSettings) -> PrimaryEngine:
        return create_engine(
            url=settings.url,
            pool_size=settings.pool_size,
            max_overflow=settings.max_overflow,
            pool_timeout=settings.pool_timeout,
            echo=settings.echo,
        )

    @provide(scope=Scope.APP)
    def get_primary_factory(self, engine: PrimaryEngine) -> PrimarySessionFactory:
        return session_factory(engine)

    @provide(scope=Scope.REQUEST)
    async def get_primary_session(self, factory: PrimarySessionFactory) -> AsyncIterator[PrimarySession]:
        async with get_session(factory) as session:
            yield session

    # ── Secondary (MySQL) — создаётся только если SECONDARY_DB_ENABLED=true ───
    @provide(scope=Scope.APP)
    def get_secondary_engine(self, settings: SecondaryDatabaseSettings) -> SecondaryEngine | None:
        if not settings.enabled:
            return None
        return create_engine(
            url=settings.url,
            pool_size=settings.pool_size,
            max_overflow=settings.max_overflow,
            pool_timeout=settings.pool_timeout,
            echo=settings.echo,
        )

    @provide(scope=Scope.APP)
    def get_secondary_factory(self, engine: SecondaryEngine | None) -> SecondarySessionFactory | None:
        if engine is None:
            return None
        return session_factory(engine)

    @provide(scope=Scope.REQUEST)
    async def get_secondary_session(
        self, factory: SecondarySessionFactory | None
    ) -> AsyncIterator[SecondarySession | None]:
        if factory is None:
            yield None
            return
        async with get_session(factory) as session:
            yield session
