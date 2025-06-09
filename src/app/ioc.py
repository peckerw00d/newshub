from typing import AsyncIterable
from dishka import Provider, Scope, from_context, provide

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from app.db.database import new_session_maker
from src.app.config import Config


class DBProvider(Provider):
    config = from_context(provides=Config, scope=Scope.APP)

    @provide(scope=Scope.APP)
    async def get_session_maker(
        self, config: Config
    ) -> async_sessionmaker[AsyncSession]:
        return await new_session_maker(config.postgres)

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self, session_maker: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AsyncSession]:
        async with session_maker() as session:
            yield session
