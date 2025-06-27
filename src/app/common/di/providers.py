from typing import AsyncIterable

from dishka import Provider, Scope, from_context, provide

from faststream.rabbit import RabbitBroker

from redis import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from src.app.db.repositories.news import NewsRepository, SourceRepository
from src.app.db.repositories.logs import UpdateLogRepository
from src.app.db.database import new_session_maker

from src.app.services.news_collector import NewsCollector
from src.app.services.source_admin import SourceAdminService
from src.app.services.news_deduplicator import Deduplicator

from src.app.common.config import Config


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

    @provide(scope=Scope.REQUEST)
    async def get_redis(self, config: Config) -> Redis:
        return Redis(
            host=config.redis.host,
            port=config.redis.port,
            db=config.redis.db,
            decode_responses=config.redis.decode_response,
        )


class RepositoryProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_source_repo(self, session: AsyncSession) -> SourceRepository:
        return SourceRepository(session=session)

    @provide(scope=Scope.REQUEST)
    async def get_news_repo(self, session: AsyncSession) -> NewsRepository:
        return NewsRepository(session=session)

    @provide(scope=Scope.REQUEST)
    async def get_logs_repo(self, session: AsyncSession) -> UpdateLogRepository:
        return UpdateLogRepository(session=session)


class ServiceProvider(Provider):
    broker = from_context(provides=RabbitBroker, scope=Scope.APP)

    @provide(scope=Scope.REQUEST)
    async def get_source_admin_service(
        self, repository: SourceRepository
    ) -> SourceAdminService:
        return SourceAdminService(repository=repository)

    @provide(scope=Scope.REQUEST)
    async def get_news_collector(
        self,
        source_repository: SourceRepository,
        news_repository: NewsRepository,
        logs_repository: UpdateLogRepository,
    ) -> NewsCollector:
        return NewsCollector(
            source_repository=source_repository,
            news_repository=news_repository,
            logs_repository=logs_repository,
        )

    @provide(scope=Scope.REQUEST)
    async def get_deduplicator(self, redis: Redis) -> Deduplicator:
        return Deduplicator(redis=redis)
