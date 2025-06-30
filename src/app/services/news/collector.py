import hashlib
import logging
import re
from dateutil.parser import parse
from typing import List, Any

import httpx
import jmespath
from asyncio import CancelledError

from src.app.db.models.news import Source
from src.app.db.repositories.base import RepositoryInterface

logger = logging.getLogger(__name__)


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

    async def _fetch_from_api(self, source: Source) -> List[dict]:
        try:
            response = await self.client.get(
                source.url, params=source.req_params, timeout=10.0
            )
            response.raise_for_status()
            json_data = response.json()

            # Определяем путь до списка статей
            first_expr = source.res_obj.get("title", "")
            # Пример: results[].title => results[]
            articles_expr = self._extract_items_path(first_expr)

            articles = jmespath.search(articles_expr, json_data)
            if not isinstance(articles, list):
                logger.warning(f"JMESPath `{articles_expr}` не вернул список.")
                return []
            return articles

        except (httpx.RequestError, httpx.HTTPStatusError) as err:
            logger.error(f"Ошибка API-запроса: {str(err)}")
            raise
        except CancelledError:
            logger.warning("Запрос был отменён (возможно, таймаут или завершение работы)")
            raise
        except Exception as e:
            logger.warning(f"Не удалось получить данные с {source.url}: {e}")
            return []

    def _extract_items_path(self, full_expr: str) -> str:
        """
        Извлекает префикс до []. Например, из 'results[].title' => 'results'
        """
        if "[]" in full_expr:
            return full_expr.split("[]")[0]
        return ""

    def _extract(self, expr: str, article: dict) -> Any:
        try:
            return jmespath.search(expr.split("[]")[-1].lstrip('.'), article)
        except Exception as e:
            logger.warning(f"JMESPath `{expr}` не удалось применить: {e}")
            return None

    async def _create_news_item(self, article: dict, source: Source):
        try:
            res_obj = source.res_obj

            published_at_raw = self._extract(res_obj["published_at"], article)
            published_at = parse(published_at_raw).replace(tzinfo=None)

            return {
                "source_id": source.id,
                "title": self._extract(res_obj["title"], article),
                "description": self._extract(res_obj["description"], article),
                "url": self._extract(res_obj["url"], article),
                "full_text": self._extract(res_obj["full_text"], article),
                "published_at": published_at,
                "hash": await self._generate_hash(article, res_obj),
            }
        except Exception as err:
            logger.error(f"Ошибка при сохранении статьи: {str(err)}")

    async def _generate_hash(self, article: dict, res_obj: dict) -> str:
        title = self._extract(res_obj["title"], article) or ""
        description = self._extract(res_obj["description"], article) or ""

        content = f"{title}{description}".lower().strip()
        normalize_text = re.sub(r"\s+", "", content)
        return hashlib.sha256(normalize_text.encode()).hexdigest()

    async def collect_news(self) -> List[dict]:
        sources = await self.source_repository.get_all()
        news_items = []

        for source in sources:
            if source.is_active:
                articles = await self._fetch_from_api(source)
                for article in articles:
                    news_item = await self._create_news_item(article, source)
                    if news_item:
                        news_items.append(news_item)

        return news_items
