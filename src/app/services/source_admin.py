from typing import List

from src.app.services.exceptions import SourceAlreadyExists, SourceNotFound
from src.app.db.models.news import Source
from src.app.db.repositories.base import RepositoryInterface
from src.app.services.dto import SourceCreateDTO, SourceResponseDTO


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
            req_params=source_data.req_params,
            res_obj=source_data.res_obj,
        )

        return await self.repository.create(source)

    async def get_all_sources(self) -> List[SourceResponseDTO]:
        sources = await self.repository.get_all()
        if not sources:
            raise SourceNotFound

        return [self.source_to_dto(source) for source in sources]

    async def delete_source(self, id: int) -> None:
        if not await self.repository.get_by_id(id=id):
            raise SourceNotFound

        return await self.repository.delete(id=id)

    def source_to_dto(source: Source) -> SourceResponseDTO:
        return SourceResponseDTO(
            id=source.id,
            name=source.name,
            url=source.url,
            type=source.type,
            poll_interval=source.poll_interval,
            last_updated=source.last_updated,
            is_active=source.is_active,
        )
