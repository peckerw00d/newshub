from typing import Optional
from sqlalchemy import Result, Select
from src.app.db.models.news import Cluster, News, Source
from src.app.db.repositories.base import Repository

from sqlalchemy.ext.asyncio import AsyncSession


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


class ClusterRepository(Repository[Cluster, int]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Cluster)
