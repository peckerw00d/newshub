import hashlib
import logging
import re
from asyncio import CancelledError
from datetime import datetime
from typing import Any, List

import feedparser
import httpx
import jmespath
from dateutil.parser import parse

from src.app.db.models import Source, UpdateLog
from src.app.db.repositories.base import RepositoryInterface

logger = logging.getLogger(__name__)


class NewsCollector:
    def __init__(
        self,
        source_repository: RepositoryInterface,
        news_repository: RepositoryInterface,
        log_repository: RepositoryInterface,
    ):
        self.source_repository = source_repository
        self.news_repository = news_repository
        self.log_repository = log_repository
        self.client = httpx.AsyncClient()

    async def _fetch_from_rss(self, source: Source) -> List[dict]:
        try:
            response = await self.client.get(source.url, timeout=10.0)
            feed = feedparser.parse(response.text)
            articles = []

            for entry in feed.entries:
                published_dt = parse(entry.get("published"))
                article = {
                    "source_id": source.id,
                    "title": entry.get("title"),
                    "description": entry.get("summary"),
                    "full_text": entry.get("summary"),
                    "url": entry.get("link"),
                    "published_at": published_dt.isoformat(),
                }
                article["hash"] = await self._generate_hash(article, {})
                articles.append(article)

            return articles
        except (httpx.RequestError, httpx.HTTPStatusError) as err:
            logger.error(f"Ошибка запроса к RSS-ленте: {str(err)}")
            raise
        except CancelledError:
            logger.warning(
                "Запрос был отменён (возможно, таймаут или завершение работы)"
            )
            raise
        except Exception as e:
            logger.warning(f"Не удалось получить данные с {source.url}: {e}")
            return []

    async def _fetch_from_api(self, source: Source) -> List[dict]:
        try:
            response = await self.client.get(
                source.url, params=source.req_params, timeout=10.0
            )
            response.raise_for_status()
            json_data = response.json()

            first_expr = source.res_obj.get("title", "")
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
            logger.warning(
                "Запрос был отменён (возможно, таймаут или завершение работы)"
            )
            raise
        except Exception as e:
            logger.warning(f"Не удалось получить данные с {source.url}: {e}")
            return []

    def _extract_items_path(self, full_expr: str) -> str:
        if "[]" in full_expr:
            return full_expr.split("[]")[0]
        return ""

    def _extract(self, expr: str, article: dict) -> Any:
        try:
            return jmespath.search(expr.split("[]")[-1].lstrip("."), article)
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

    async def _generate_hash(self, article: dict, res_obj: dict | None) -> str:
        if res_obj:
            title = self._extract(res_obj["title"], article) or ""
            description = self._extract(res_obj["description"], article) or ""
        else:
            title = article.get("title", "") or ""
            description = article.get("description", "") or ""
        content = f"{title}{description}".lower().strip()
        normalize_text = re.sub(r"\s+", "", content)
        return hashlib.sha256(normalize_text.encode()).hexdigest()

    async def collect_news(self) -> List[dict]:
        sources = await self.source_repository.get_all()
        news_items = []

        for source in sources:
            if not source.is_active:
                continue

            start_time = datetime.now()
            update_log_data = {
                "source_id": source.id,
                "status": "started",
                "start_time": start_time,
            }
            if source.type == "api":
                try:
                    log_entry = await self.log_repository.create(
                        UpdateLog(**update_log_data)
                    )

                    articles = await self._fetch_from_api(source)

                    for article in articles:
                        news_item = await self._create_news_item(article, source)
                        if news_item:
                            news_items.append(news_item)

                    await self.log_repository.update(
                        log_entry.id,
                        {
                            "status": "success",
                            "end_time": datetime.now(),
                            "error_message": None,
                        },
                    )

                except Exception as err:
                    logger.error(
                        f"Error collecting news from source {source.name}: {err}"
                    )
                    await self.log_repository.update(
                        log_entry.id,
                        {
                            "status": "failed",
                            "end_time": datetime.now(),
                            "error_message": str(err),
                        },
                    )
            elif source.type == "rss":
                try:
                    log_entry = await self.log_repository.create(
                        UpdateLog(**update_log_data)
                    )

                    articles = await self._fetch_from_rss(source)
                    for article in articles:
                        news_items.append(article)

                    await self.log_repository.update(
                        log_entry.id,
                        {
                            "status": "success",
                            "end_time": datetime.now(),
                            "error_message": None,
                        },
                    )
                except Exception as err:
                    logger.error(
                        f"Error collecting news from source {source.name}: {err}"
                    )
                    await self.log_repository.update(
                        log_entry.id,
                        {
                            "status": "failed",
                            "end_time": datetime.now(),
                            "error_message": str(err),
                        },
                    )

        return news_items
