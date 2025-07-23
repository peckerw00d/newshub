import logging

import jmespath
from dateutil.parser import parse

logger = logging.getLogger(__name__)


class ArticleExtractor:
    def extract(self, expr: str, article: dict) -> str | None:
        try:
            return jmespath.search(expr.split("[]")[-1].lstrip("."), article)
        except Exception as e:
            logger.warning(f"JMESPath `{expr}` не удалось применить: {e}")
            return None

    def parse_date(self, raw_date: str) -> str:
        return parse(raw_date).replace(tzinfo=None)
