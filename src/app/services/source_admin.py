from typing import List
from src.app.db.models.news import Source
from src.app.db.repositories.base import RepositoryInterface
from src.app.services.dto import SourceDTO


class SourceAdminService:
    def __init__(self, repository: RepositoryInterface):
        self.repository = repository

    async def add_source(self, source_data: SourceDTO) -> Source:
        source = Source(
            name=source_data.name,
            url=source_data.url,
            type=source_data.type,
            last_updated=source_data.last_updated,
            poll_interval=source_data.poll_interval,
            is_active=source_data.is_active,
        )

        return self.repository.create(source)

    async def get_all_sources(self, source_data: SourceDTO) -> List[Source]:
        return self.repository.get_all()

    async def delete_source(self, source_id: int) -> None:
        return self.repository.delete(id=source_id)
