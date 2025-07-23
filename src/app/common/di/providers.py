from typing import AsyncIterable

from dishka import Provider, Scope, from_context, provide
from faststream.rabbit import RabbitBroker
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.services.collectors.rss_collector import RSSCollector
from src.app.common.config import Config
from src.app.db.database import new_session_maker
from src.app.db.repositories.logs import UpdateLogRepository
from src.app.db.repositories.news import NewsRepository, SourceRepository
from src.app.services.admin.source import SourceAdminService
from src.app.services.collectors.api_collector import APICollector
from src.app.services.collectors.article_extractor import ArticleExtractor
from src.app.services.hash_service import HashService
from src.app.services.news import NewsService
from src.app.services.news_pipeline.collector import NewsCollector
from src.app.services.news_pipeline.deduplicator import Deduplicator


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
    extractor = provide(ArticleExtractor, scope=Scope.REQUEST)
    hash_service = provide(HashService, scope=Scope.REQUEST)

    @provide(scope=Scope.REQUEST)
    async def get_source_admin_service(
        self, repository: SourceRepository
    ) -> SourceAdminService:
        return SourceAdminService(repository=repository)

    @provide(scope=Scope.REQUEST)
    async def get_news_service(self, repository: NewsRepository) -> NewsService:
        return NewsService(news_repository=repository)

    @provide(scope=Scope.REQUEST)
    async def get_api_collector(
        self, extractor: ArticleExtractor, hash_service: HashService
    ) -> APICollector:
        return APICollector(extractor=extractor, hash_service=hash_service)

    @provide(scope=Scope.REQUEST)
    async def get_rss_collector(
        self,
        hash_service: HashService,
    ) -> RSSCollector:
        return RSSCollector(hash_service=hash_service)

    @provide(scope=Scope.REQUEST)
    async def get_news_collector(
        self,
        source_repository: SourceRepository,
        news_repository: NewsRepository,
        log_repository: UpdateLogRepository,
        extractor: ArticleExtractor,
        hash_service: HashService,
        api_collector: APICollector,
        rss_collector: RSSCollector,
    ) -> NewsCollector:
        return NewsCollector(
            source_repo=source_repository,
            news_repo=news_repository,
            log_repo=log_repository,
            extractor=extractor,
            hash_service=hash_service,
            api_collector=api_collector,
            rss_collector=rss_collector,
        )

    @provide(scope=Scope.REQUEST)
    async def get_deduplicator(self, redis: Redis) -> Deduplicator:
        return Deduplicator(redis=redis)
