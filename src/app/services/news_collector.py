import hashlib
from datetime import datetime
from dateutil.parser import parse
from os import getenv
from typing import List

import httpx

from src.app.db.models.news import News, Source
from src.app.db.repositories.base import RepositoryInterface


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
        self.client = httpx.AsyncClient()

    async def _fetch_from_api(self, source: Source):
        try:
            response = await self.client.get(
                source.url, params=source.req_params, timeout=10.0
            )
            response.raise_for_status()
            return response.json().get(source.res_obj.get("result", ""), [])

        except (httpx.RequestError, httpx.HTTPStatusError) as err:
            raise Exception(f"API request failed: {str(err)}") from err

    async def _save_news(self, news_data: List[dict], source: Source):
        for article in news_data:
            try:
                published_at = parse(article[source.res_obj["published_at"]]).replace(
                    tzinfo=None
                )

                news = News(
                    source_id=source.id,
                    title=article[source.res_obj["title"]],
                    description=article[source.res_obj["description"]],
                    url=article[source.res_obj["url"]],
                    full_text=article[source.res_obj["full_text"]],
                    published_at=published_at,
                    hash=await self._generate_hash(article, source.res_obj),
                )
                await self.news_repository.create(news)

            except Exception as err:
                print(f"Error saving article: {str(err)}")
                continue

        source.last_fetched = datetime.now()
        await self.source_repository.update(source)

    async def _generate_hash(self, article: dict, res_obj: dict) -> str:
        content = (
            f"{article[res_obj['title']]}{article.get(res_obj['description'], '')}"
        )
        return hashlib.md5(content.encode()).hexdigest()

    async def collect_news(self) -> List[News]:
        sources = await self.source_repository.get_all()
        for source in sources:
            if source.is_active:
                news_data = await self._fetch_from_api(source)
                await self._save_news(news_data, source)