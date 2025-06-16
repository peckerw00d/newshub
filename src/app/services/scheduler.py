from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor

from app.db.models.logs import UpdateLog
from app.db.models.news import Source
from src.app.services.news_collector import NewsCollector
from src.app.db.repositories.base import RepositoryInterface
from src.app.config import Config


class Scheduler:
    def __init__(
        self,
        config: Config,
        source_repository: RepositoryInterface,
        logs_repository: RepositoryInterface,
        collector: NewsCollector,
    ):
        self.source_repository = source_repository
        self.logs_repository = logs_repository
        self.collector = collector
        self.config = config
        self.scheduler = AsyncIOScheduler(
            jobstores={"default": SQLAlchemyJobStore(config.postgres.url)},
            executors={"default": AsyncIOExecutor()},
        )

    async def start(self):
        await self.scheduler.start()

        sources = await self._get_all_sources()
        for source in sources:
            await self.schedule_source(
                source_id=source.id, interval=source.poll_interval
            )

    async def schedule_source(self, source_id: int, interval: float):
        job_id = f"source_{source_id}"

        await self.scheduler.add_job(
            self._run_collector,
            trigger="interval",
            seconds=interval,
            id=job_id,
            args=[source_id],
            replace_existing=True,
            max_instances=self.config.SCHEDULER_MAX_INSTANCES,
        )

    async def _run_collector(self, source_id: int):
        try:
            await self.collector.collect_news()

        except Exception as e:
            await self._handle_error(source_id, str(e))
            raise

    async def _handle_error(self, source: Source, error_msg: str) -> None:
        log = UpdateLog(
            source_id=source.id,
            start_time=datetime.now(),
            end_time=datetime.now(),
            status="failed",
            error_message=error_msg,
        )
        await self.logs_repository.create(log)

    async def shutdown(self):
        await self.scheduler.shutdown()
