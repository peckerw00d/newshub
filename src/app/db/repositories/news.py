from src.app.db.models.news import Cluster, News, Source
from src.app.db.repositories.base import Repository

from sqlalchemy.ext.asyncio import AsyncSession


class SourceRepository(Repository[Source, int]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Source)


class NewsRepository(Repository[News, int]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, News)


class ClusterRepository(Repository[Cluster, int]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Cluster)
