from fastapi import APIRouter, HTTPException, status
from dishka.integrations.fastapi import DishkaRoute, FromDishka

from src.app.services.exceptions import SourceAlreadyExists
from src.app.api.schemas import SourceAdminCreate
from src.app.services.source_admin import SourceAdminService
from src.app.services.dto import SourceCreateDTO


router = APIRouter(route_class=DishkaRoute)


@router.post("/")
async def add_source(
    data: SourceAdminCreate, source_admin_service: FromDishka[SourceAdminService]
):
    try:
        source_data = SourceCreateDTO(**data.model_dump())
        new_source = await source_admin_service.add_source(source_data=source_data)
        return {"message": "The source was added successfully!"}
    except SourceAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="The source already exists!"
        )
