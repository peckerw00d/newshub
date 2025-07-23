import logging

import httpx
import jmespath

from src.app.services.collectors.article_extractor import ArticleExtractor
from src.app.services.hash_service import HashService

logger = logging.getLogger(__name__)


class APICollector:
    def __init__(
        self,
        extractor: ArticleExtractor,
        hash_service: HashService,
        client: httpx.AsyncClient | None = None,
    ):
        self.client = client
        self.extractor = extractor
        self.hash_service = hash_service

    def _extract_items_path(self, expr: str) -> str:
        return expr.split("[]")[0] if "[]" in expr else ""

    async def fetch(self, source) -> list[dict]:
        try:
            params = source.req_params or {}
            res_obj = source.res_obj or {}

            response = await self.client.get(source.url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()

            path = self._extract_items_path(res_obj.get("title", ""))
            items = jmespath.search(path, data)

            if not isinstance(items, list):
                logger.warning(f"JMESPath `{path}` не вернул список.")
                return []

            return items

        except Exception as e:
            logger.warning(f"Ошибка при получении API: {e}")
            return []
