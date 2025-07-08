from fastapi import APIRouter, HTTPException, status
from dishka.integrations.fastapi import DishkaRoute, FromDishka

from src.app.services.exceptions import SourceAlreadyExists, SourceNotFound
from src.app.api.schemas import SourceAdminCreate, SourceAdminResponse, SourceAdminUpdate
from src.app.services.source_admin import SourceAdminService
from src.app.services.dto import SourceCreateDTO


router = APIRouter(route_class=DishkaRoute, prefix="/admin", tags=["Admin"])


@router.post("/sources")
async def add_source(
    data: SourceAdminCreate, source_admin_service: FromDishka[SourceAdminService]
):
    try:
        source_data = SourceCreateDTO(**data.model_dump())
        await source_admin_service.add_source(source_data=source_data)
        return {"message": "The source was added successfully!"}

    except SourceAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="The source already exists!"
        )


@router.get("/sources")
async def get_all_sources(source_admin_service: FromDishka[SourceAdminService]):
    try:
        sources_dto = await source_admin_service.get_all_sources()
        return [
            SourceAdminResponse(
                id=dto.id,
                name=dto.name,
                url=dto.url,
                type=dto.type,
                poll_interval=dto.poll_interval,
                is_active=dto.is_active,
                last_updated=dto.last_updated,
            )
            for dto in sources_dto
        ]

    except SourceNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No sources found!"
        )


@router.get("/sources/{id}")
async def get_source(id: int, source_admin_service: FromDishka[SourceAdminService]):
    try:
        source_dto = await source_admin_service.get_source(id=id)
        return SourceAdminResponse(
            id=source_dto.id,
            name=source_dto.name,
            url=source_dto.url,
            type=source_dto.type,
            poll_interval=source_dto.poll_interval,
            is_active=source_dto.is_active,
            last_updated=source_dto.last_updated,
        )

    except SourceNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No sources found!"
        )

@router.put("/sources/{id}")
async def update_source(id: int, data: SourceAdminUpdate, source_admin_service: FromDishka[SourceAdminService]):
    try:
        return await source_admin_service.update_source(id=id, data=data)

    except SourceNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No sources found!"
        )

@router.delete("/sources/{id}")
async def delete_source(id: int, source_admin_service: FromDishka[SourceAdminService]):
    try:
        return await source_admin_service.delete_source(id=id)

    except SourceNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No sources found!"
        )
