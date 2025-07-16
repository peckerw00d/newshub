from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from src.app.api.schemas.news import NewsCursorPage, NewsResponse
from src.app.common.pagination import decode_cursor, encode_cursor
from src.app.services.news import NewsService

router = APIRouter(
    route_class=DishkaRoute,
    prefix="/news",
    tags=[
        "News",
    ],
)


@router.get("/")
async def get_news(
    news_service: FromDishka[NewsService], cursor: str | None = None, limit: int = 20
):
    cursor = decode_cursor(cursor) if cursor else None

    news, next_cursor_tuple = await news_service.get_news(limit, cursor)

    if next_cursor_tuple:
        next_cursor = encode_cursor(next_cursor_tuple[0], next_cursor_tuple[1])
    else:
        next_cursor = None
    items = [
        NewsResponse(
            title=item.title,
            description=item.description,
            url=item.url,
            published_at=item.published_at,
        )
        for item in news
    ]
    return NewsCursorPage(items=items, next_cursor=next_cursor if news else None)


@router.get("/search")
async def search_news(
    news_service: FromDishka[NewsService],
    query: str,
    cursor: str | None = None,
    limit: int = 20,
):
    cursor = decode_cursor(cursor) if cursor else None

    news, next_cursor_tuple = await news_service.search_news(query, limit, cursor)

    if next_cursor_tuple:
        next_cursor = encode_cursor(next_cursor_tuple[0], next_cursor_tuple[1])
    else:
        next_cursor = None
    items = [
        NewsResponse(
            title=item.title,
            description=item.description,
            url=item.url,
            published_at=item.published_at,
        )
        for item in news
    ]
    return NewsCursorPage(items=items, next_cursor=next_cursor if news else None)
