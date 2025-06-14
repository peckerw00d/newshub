from typing import AsyncIterable
from dishka import Provider, Scope, from_context, provide

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from src.app.services.source_admin import SourceAdminService
from src.app.db.database import new_session_maker
from src.app.db.repositories.news import SourceRepository
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


class RepositoryProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_source_repo(self, session: AsyncSession) -> SourceRepository:
        return SourceRepository(session=session)


class ServiceProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_source_admin_service(
        self, repository: SourceRepository
    ) -> SourceAdminService:
        return SourceAdminService(repository=repository)
