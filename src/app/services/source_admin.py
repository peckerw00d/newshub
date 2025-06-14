from typing import List
from src.app.services.exceptions import SourceAlreadyExists
from src.app.db.models.news import Source
from src.app.db.repositories.base import RepositoryInterface
from src.app.services.dto import SourceCreateDTO


class SourceAdminService:
    def __init__(self, repository: RepositoryInterface):
        self.repository = repository

    async def add_source(self, source_data: SourceCreateDTO) -> Source:
        if await self.repository.get_source_by_url(source_data.url):
            raise SourceAlreadyExists

        source = Source(
            name=source_data.name,
            url=source_data.url,
            type=source_data.type,
            poll_interval=source_data.poll_interval,
        )

        return await self.repository.create(source)

    async def get_all_sources(self, source_data: SourceCreateDTO) -> List[Source]:
        return self.repository.get_all()

    async def delete_source(self, source_id: int) -> None:
        return self.repository.delete(id=source_id)
