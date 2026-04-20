from __future__ import annotations

from datetime import date, datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Enum, ForeignKey, Index, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.fortune import DailyFortune
    from app.models.log import FortuneLog
    from app.models.user import User


class Gender(str, PyEnum):
    MALE = "MALE"
    FEMALE = "FEMALE"


class CalendarType(str, PyEnum):
    SOLAR = "SOLAR"
    LUNAR = "LUNAR"


class SajuProfile(Base):
    __tablename__ = "saju_profiles"
    __table_args__ = (Index("idx_profiles_email", "user_email"),)

    profile_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_email: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("users.email", ondelete="CASCADE"),
        nullable=False,
    )
    nickname: Mapped[str] = mapped_column(String(50), nullable=False)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    birth_time: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        server_default=text("'UNKNOWN'"),
    )
    gender: Mapped[Gender] = mapped_column(
        Enum(Gender, native_enum=False, values_callable=lambda obj: [item.value for item in obj]),
        nullable=False,
    )
    calendar_type: Mapped[CalendarType] = mapped_column(
        Enum(
            CalendarType,
            native_enum=False,
            values_callable=lambda obj: [item.value for item in obj],
        ),
        nullable=False,
        server_default=CalendarType.SOLAR.value,
    )

    year_ganji: Mapped[str | None] = mapped_column(String(10))
    month_ganji: Mapped[str | None] = mapped_column(String(10))
    day_ganji: Mapped[str | None] = mapped_column(String(10))
    time_ganji: Mapped[str | None] = mapped_column(String(10))

    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship("User", back_populates="saju_profiles", lazy="selectin")
    daily_fortunes: Mapped[list["DailyFortune"]] = relationship(
        "DailyFortune",
        back_populates="profile",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )
    fortune_logs: Mapped[list["FortuneLog"]] = relationship(
        "FortuneLog",
        back_populates="profile",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )
