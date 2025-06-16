import hashlib
from datetime import datetime
from os import getenv
from typing import List

import httpx

from src.app.db.models.logs import UpdateLog
from src.app.db.models.news import News, Source
from src.app.db.repositories.base import RepositoryInterface
from src.app.services.exceptions import SourceNotFound


NEWSAPI_KEY = getenv("NEWSAPI_KEY")
NEWSAPI_URL = "https://newsapi.org/v2/top-headlines"


class NewsCollector:
    def __init__(
        self,
        source_repository: RepositoryInterface,
        news_repository: RepositoryInterface,
        logs_repository: RepositoryInterface,
    ):
        self.source_repository = source_repository
        self.news_repository = news_repository
        self.logs_repository = logs_repository
        self.params = {"apiKey": NEWSAPI_KEY, "country": "us", "pageSize": 20}
        self.client = httpx.AsyncClient()

    async def _get_source(self):
        source = await self.source_repository.get_source_by_url(NEWSAPI_URL)
        if not source:
            raise SourceNotFound(f"Source not found for URL: {NEWSAPI_URL}")
        return source

    async def _fetch_from_api(self):
        try:
            response = await self.client.get(
                NEWSAPI_URL, params=self.params, timeout=10.0
            )
            response.raise_for_status()
            return response.json().get("articles", [])

        except (httpx.RequestError, httpx.HTTPStatusError) as err:
            raise Exception(f"API request failed: {str(err)}") from err

    async def _save_news(self, news_data: List[dict], source: Source):
        for article in news_data:
            try:
                published_at = datetime.strptime(
                    article["publishedAt"], "%Y-%m-%dT%H:%M:%SZ"
                )

                news = News(
                    source_id=source.id,
                    title=article["title"],
                    description=article["description"],
                    url=article["url"],
                    published_at=published_at,
                    hash=await self._generate_hash(article),
                )
                await self.news_repository.create(news)

            except Exception as err:
                print(f"Error saving article: {str(err)}")
                continue

        source.last_fetched = datetime.now()
        await self.source_repository.update(source)

    async def _generate_hash(self, article: dict) -> str:
        content = f"{article['title']}{article.get('description', '')}"
        return hashlib.md5(content.encode()).hexdigest()

    async def _handle_error(self, source: Source, error_msg: str) -> None:
        log = UpdateLog(
            source_id=source.id,
            start_time=datetime.now(),
            end_time=datetime.now(),
            status="failed",
            error_message=error_msg,
        )
        await self.logs_repository.create(log)

    async def collect_news(self) -> List[News]:
        try:
            source = await self._get_source()
            news_data = await self._fetch_from_api()
            await self._save_news(news_data, source)

        except Exception as err:
            await self._handle_error(source, str(err))
            raise
