from typing import List

from src.app.db.models.news import Source
from src.app.db.repositories.base import RepositoryInterface
from src.app.services.dto import SourceCreateDTO, SourceResponseDTO, SourceUpdateDTO
from src.app.services.exceptions import SourceAlreadyExists, SourceNotFound


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

    async def get_source(self, id: int) -> SourceResponseDTO:
        source = await self.repository.get_by_id(id=id)
        if not source:
            raise SourceNotFound

        return self.source_to_dto(source)

    async def update_source(
        self, id: int, source_data: SourceUpdateDTO
    ) -> SourceResponseDTO:
        source = await self.repository.get_by_id(id=id)
        if not source:
            raise SourceNotFound

        source.name = source_data.name
        source.url = source_data.url
        source.type = source_data.type
        source.poll_interval = source_data.poll_interval
        source.req_params = source_data.req_params
        source.res_obj = source_data.res_obj
        source.is_active = source_data.is_active

        updated_source = await self.repository.update(id, data.__dict__)

        return self.source_to_dto(updated_source)

    async def delete_source(self, id: int) -> None:
        if not await self.repository.get_by_id(id=id):
            raise SourceNotFound

        return await self.repository.delete(id=id)

    def source_to_dto(self, source: Source) -> SourceResponseDTO:
        return SourceResponseDTO(
            id=source.id,
            name=source.name,
            url=source.url,
            type=source.type,
            poll_interval=source.poll_interval,
            last_updated=source.last_updated,
            is_active=source.is_active,
            req_params=source.req_params,
            res_obj=source.res_obj,
        )
