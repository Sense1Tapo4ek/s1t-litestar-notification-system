from typing import AsyncIterable
from dishka import Provider, Scope, provide
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from .config import GenericConfig
from core.adapters.driven.db.orm_models import Base as CoreBase
from notifications.adapters.driven.db.orm_models import Base as NotificationsBase


class SharedProvider(Provider):
    scope = Scope.APP

    @provide(scope=Scope.APP)
    def provide_config(self) -> GenericConfig:
        return GenericConfig()

    @provide(scope=Scope.APP)
    async def provide_engine(self, config: GenericConfig) -> AsyncIterable[AsyncEngine]:
        config.volume_path.mkdir(parents=True, exist_ok=True)
        engine = create_async_engine(config.db_url, echo=False)

        @event.listens_for(engine.sync_engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.close()

        async with engine.begin() as conn:
            await conn.run_sync(CoreBase.metadata.create_all)
            await conn.run_sync(NotificationsBase.metadata.create_all)

        yield engine
        await engine.dispose()

    @provide(scope=Scope.APP)
    def provide_sessionmaker(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    @provide(scope=Scope.REQUEST)
    async def provide_session(self, sessionmaker: async_sessionmaker[AsyncSession]) -> AsyncIterable[AsyncSession]:
        async with sessionmaker() as session:
            yield session
