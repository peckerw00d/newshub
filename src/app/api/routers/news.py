from fastapi import APIRouter
from dishka.integrations.fastapi import DishkaRoute, FromDishka

from src.app.services.news_collector import NewsCollector


router = APIRouter(
    route_class=DishkaRoute,
    prefix="/news",
    tags=[
        "News",
    ],
)


@router.post("/fetch_news")
async def fetch_news(fetcher: FromDishka[NewsCollector]):
    await fetcher.collect_news()
    return {"message": "News fetching completed successfully"}
