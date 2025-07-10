from datetime import datetime
from typing import Optional

from sqlalchemy import Result, Select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.db.models.news import Cluster, News, Source
from src.app.db.repositories.base import Repository


class SourceRepository(Repository[Source, int]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Source)

    async def get_source_by_url(self, url: str) -> Optional[Source]:
        stmt = Select(Source).where(Source.url == url)
        result: Result = await self.session.execute(stmt)
        return result.scalars().first()


class NewsRepository(Repository[News, int]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, News)

    async def paginate_news_by_datetime(
        self, limit: int, cursor: tuple[datetime, str] | None = None
    ):
        published_at = News.published_at
        hash = News.hash

        stmt = Select(News)
        order = [published_at.desc(), hash.desc()]

        if cursor:
            cursor_created_at, cursor_hash = cursor
            stmt = stmt.where(
                tuple_(published_at, hash) < (cursor_created_at, cursor_hash)
            )

        stmt = stmt.order_by(*order).limit(limit)
        result: Result = await self.session.execute(stmt)
        items = result.scalars().all()

        if items:
            last = items[-1]
            next_cursor = (getattr(last, published_at.key), getattr(last, hash.key))
        else:
            next_cursor = None

        return items, next_cursor


class ClusterRepository(Repository[Cluster, int]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Cluster)
