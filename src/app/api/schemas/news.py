from datetime import datetime

from pydantic import BaseModel


class NewsResponse(BaseModel):
    title: str
    description: str | None
    url: str
    published_at: datetime


class NewsCursorPage(BaseModel):
    items: list[NewsResponse]
    next_cursor: str | None = None
