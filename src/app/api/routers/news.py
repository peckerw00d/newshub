from fastapi import APIRouter
from dishka.integrations.fastapi import DishkaRoute, FromDishka

from src.app.services.tasks.rabbit_publisher import RabbitPublisher


router = APIRouter(
    route_class=DishkaRoute,
    prefix="/news",
    tags=[
        "News",
    ],
)


@router.post("/fetch_news")
async def fetch_news(publisher: FromDishka[RabbitPublisher]):
    await publisher.publish_fetch_news_task()
    return {"message": "News fetching completed successfully"}
