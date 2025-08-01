from typing import List

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.db.models import Base


class Tag(Base):
    __tablename__ = "tags"

    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    news: Mapped[List["News"]] = relationship(
        secondary="news_tags", back_populates="tags", lazy="raise"
    )


class NewsTag(Base):
    __tablename__ = "news_tags"

    news_id: Mapped[int] = mapped_column(ForeignKey("news.id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), primary_key=True)
