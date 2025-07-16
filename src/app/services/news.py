from datetime import datetime

from src.app.db.repositories.base import RepositoryInterface


class NewsService:
    def __init__(self, news_repository: RepositoryInterface) -> None:
        self.news_repository = news_repository

    async def get_news(self, limit: int, cursor: tuple[datetime, str] | None = None):
        return await self.news_repository.paginate_news_by_datetime(limit, cursor)

    async def search_news(
        self, query: str, limit: int, cursor: tuple[datetime, str] | None = None
    ):
        return await self.news_repository.search_news_by_text(query, limit, cursor)
