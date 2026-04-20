from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.saju import SajuProfile


class DailyFortune(Base):
    __tablename__ = "daily_fortunes"
    __table_args__ = (
        UniqueConstraint("profile_id", "target_date", name="idx_fortunes_lookup"),
    )

    fortune_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("saju_profiles.profile_id", ondelete="CASCADE"),
        nullable=False,
    )
    target_date: Mapped[date] = mapped_column(Date, nullable=False)
    fortune_score: Mapped[int] = mapped_column(Integer, nullable=False)
    money_score: Mapped[int] = mapped_column(Integer, nullable=False)
    love_score: Mapped[int] = mapped_column(Integer, nullable=False)
    health_score: Mapped[int] = mapped_column(Integer, nullable=False)
    work_score: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    advice: Mapped[str] = mapped_column(Text, nullable=False)
    luck_item: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(10), server_default="SUCCESS", nullable=False)
    error_msg: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    profile: Mapped["SajuProfile"] = relationship(
        "SajuProfile",
        back_populates="daily_fortunes",
        lazy="selectin",
    )


class FortunePhrase(Base):
    __tablename__ = "fortune_phrases"

    phrase_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    category: Mapped[str] = mapped_column(String(20), nullable=False)
    mood: Mapped[str] = mapped_column(String(10), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
