from fastapi import APIRouter
from dishka.integrations.fastapi import DishkaRoute


router = APIRouter(
    route_class=DishkaRoute,
    prefix="/news",
    tags=[
        "News",
    ],
)
