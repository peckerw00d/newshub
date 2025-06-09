import datetime
from src.app.db.models import Base

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class UpdateLog(Base):
    __tablename__ = "update_logs"

    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False)
    start_time: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[datetime.datetime | None] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text)
    source: Mapped["Source"] = relationship(back_populates="update_log")
