import datetime
from typing import List

from sqlalchemy import (
    ARRAY,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.services.dto import SourceResponseDTO
from src.app.db.models.base import Base


class Source(Base):
    __tablename__ = "sources"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(512), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    last_updated: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    poll_interval: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    news: Mapped[List["News"]] = relationship(back_populates="source")
    update_log: Mapped[List["UpdateLog"]] = relationship(back_populates="source")

    def to_response_dto(self) -> SourceResponseDTO:
        return SourceResponseDTO(
            id=self.id,
            name=self.name,
            url=self.url,
            type=self.type,
            poll_interval=self.poll_interval,
            last_updated=self.last_updated,
            is_active=self.is_active,
        )


class News(Base):
    __tablename__ = "news"

    source_id: Mapped[int | None] = mapped_column(ForeignKey("sources.id"))
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    full_text: Mapped[str | None] = mapped_column(Text)
    url: Mapped[str] = mapped_column(String(512), nullable=False)
    published_at: Mapped[datetime.datetime] = mapped_column(DateTime)
    cluster_id: Mapped[int | None] = mapped_column(ForeignKey("clusters.id"))
    sentiment_score: Mapped[float | None] = mapped_column(Float)
    sentiment_label: Mapped[str | None] = mapped_column(String(50))
    hash: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    source: Mapped["Source"] = relationship(back_populates="news")
    cluster: Mapped["Cluster"] = relationship(back_populates="news")
    tags: Mapped[List["Tag"]] = relationship(
        secondary="news_tags", back_populates="news", lazy="raise"
    )


class Cluster(Base):
    __tablename__ = "clusters"

    topic: Mapped[str] = mapped_column(Text, nullable=False)
    keywords: Mapped[List[str]] = mapped_column(ARRAY(Text))
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    news: Mapped[List["News"]] = relationship(back_populates="cluster")
