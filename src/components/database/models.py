from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String

from sqlalchemy.orm import Mapped, mapped_column

from .connection import Base

class BeatmapSet(Base):
    __tablename__ = "beatmapsets"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    title: Mapped[str] = mapped_column(String(255))
    artist: Mapped[str] = mapped_column(String(255))
    creator: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(255))

    discovered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    notification_status: Mapped[str] = mapped_column(String(20), default="pending", index=True)