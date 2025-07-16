from datetime import datetime
from typing import Optional

from sqlalchemy import Result, Select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import func, text

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

    async def _execute_paginated_query(
        self,
        base_stmt: Select,
        limit: int,
        cursor: tuple[datetime, str] | None,
    ):
        published_at = News.published_at
        hash = News.hash

        if cursor:
            cursor_created_at, cursor_hash = cursor
            base_stmt = base_stmt.where(
                tuple_(published_at, hash) < (cursor_created_at, cursor_hash)
            )

        base_stmt = base_stmt.order_by(published_at.desc(), hash.desc()).limit(limit)

        result = await self.session.execute(base_stmt)
        items = result.scalars().all()

        next_cursor = None
        if items:
            last = items[-1]
            next_cursor = (getattr(last, published_at.key), getattr(last, hash.key))

        return items, next_cursor

    async def paginate_news_by_datetime(
        self, limit: int, cursor: tuple[datetime, str] | None = None
    ):
        stmt = Select(News)
        return await self._execute_paginated_query(stmt, limit, cursor)

    async def search_news_by_text(
        self, query: str, limit: int, cursor: tuple[datetime, str] | None = None
    ):
        search_vector = func.setweight(
            func.to_tsvector("english", func.coalesce(News.title, "")), text("'A'")
        ).op("||")(
            func.setweight(
                func.to_tsvector("english", func.coalesce(News.description, "")),
                text("'B'"),
            )
        )
        ts_query = func.plainto_tsquery("english", query)

        stmt = Select(News).where(search_vector.op("@@")(ts_query))

        return await self._execute_paginated_query(stmt, limit, cursor)


class ClusterRepository(Repository[Cluster, int]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Cluster)
