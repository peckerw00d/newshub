import logging

import feedparser
import httpx
from dateutil.parser import parse

from app.services.hash_service import HashService

logger = logging.getLogger(__name__)


class RSSCollector:
    def __init__(
        self, hash_service: HashService, client: httpx.AsyncClient | None = None
    ):
        self.client = client
        self.hash_service = hash_service

    async def fetch(self, source) -> list[dict]:
        try:
            response = await self.client.get(source.url, timeout=10.0)
            feed = feedparser.parse(response.text)
            articles = []
            for entry in feed.entries:
                published_dt = parse(entry.get("published")).replace(tzinfo=None)
                article = {
                    "source_id": source.id,
                    "title": entry.get("title"),
                    "description": entry.get("summary"),
                    "full_text": entry.get("summary"),
                    "url": entry.get("link"),
                    "published_at": published_dt.isoformat(),
                }
                content = f"{article['title']}{article['description']}"
                article["hash"] = self.hash_service.generate(content)
                articles.append(article)
            return articles
        except Exception as e:
            logger.warning(f"Ошибка при получении RSS: {e}")
            return []
