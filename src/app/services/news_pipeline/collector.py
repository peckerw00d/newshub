import logging
from datetime import datetime

import httpx

from src.app.db.models.logs import UpdateLog
from src.app.db.repositories.logs import UpdateLogRepository
from src.app.db.repositories.news import NewsRepository, SourceRepository
from src.app.services.collectors.api_collector import APICollector
from src.app.services.collectors.article_extractor import ArticleExtractor
from src.app.services.collectors.rss_collector import RSSCollector
from src.app.services.hash_service import HashService

logger = logging.getLogger(__name__)


class NewsCollector:
    def __init__(
        self,
        source_repo: SourceRepository,
        news_repo: NewsRepository,
        log_repo: UpdateLogRepository,
        extractor: ArticleExtractor,
        hash_service: HashService,
        rss_collector: RSSCollector,
        api_collector: APICollector,
    ):
        self.source_repo = source_repo
        self.news_repo = news_repo
        self.log_repo = log_repo

        self.client = httpx.AsyncClient()
        self.extractor = extractor
        self.hash_service = hash_service

        self.rss_collector = rss_collector
        self.api_collector = api_collector

    async def _create_news_item(self, article: dict, source) -> dict:
        try:
            res = source.res_obj or {}
            published_raw = self.extractor.extract(res["published_at"], article)
            published_at = self.extractor.parse_date(published_raw)
            title = self.extractor.extract(res["title"], article) or ""
            description = self.extractor.extract(res["description"], article) or ""
            url = self.extractor.extract(res["url"], article)
            full_text = self.extractor.extract(res["full_text"], article)
            content = f"{title}{description}"
            return {
                "source_id": source.id,
                "title": title,
                "description": description,
                "url": url,
                "full_text": full_text,
                "published_at": published_at,
                "hash": self.hash_service.generate(content),
            }
        except Exception as e:
            logger.error(f"Ошибка при формировании новости: {e}")

    async def collect_news(self):
        sources = await self.source_repo.get_all()
        news_items = []

        for source in sources:
            if not source.is_active:
                continue

            log = await self.log_repo.create(
                UpdateLog(
                    **{
                        "source_id": source.id,
                        "status": "started",
                        "start_time": datetime.now(),
                    }
                )
            )

            try:
                if source.type == "rss":
                    articles = await self.rss_collector.fetch(source)
                    news_items.extend(articles)
                elif source.type == "api":
                    raw_articles = await self.api_collector.fetch(source)
                    for raw_article in raw_articles:
                        item = await self._create_news_item(raw_article, source)
                        if item:
                            news_items.append(item)

                await self.log_repo.update(
                    log.id,
                    {
                        "status": "success",
                        "end_time": datetime.now(),
                        "error_message": None,
                    },
                )
            except Exception as e:
                logger.error(f"Ошибка источника {source.name}: {e}")
                await self.log_repo.update(
                    log.id,
                    {
                        "status": "failed",
                        "end_time": datetime.now(),
                        "error_message": str(e),
                    },
                )

        return news_items
