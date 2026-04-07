from __future__ import annotations
from datetime import date
from enum import Enum as PyEnum
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Date, Boolean, Enum, BigInteger, Index, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base

from app.models.fortune import DailyFortune

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.log import FortuneLog


class Gender(str, PyEnum):
    MALE = "MALE"
    FEMALE = "FEMALE"


class SajuProfile(Base):
    """사주 프로필 (간지 데이터 캐싱 포함)"""

    __tablename__ = "saju_profiles"
    __table_args__ = (Index("idx_profiles_email", "user_email"),)

    profile_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
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
        Enum(
            Gender,
            native_enum=False,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
    )

    # 간지 데이터 (캐싱용)
    year_ganji: Mapped[Optional[str]] = mapped_column(String(10))
    month_ganji: Mapped[Optional[str]] = mapped_column(String(10))
    day_ganji: Mapped[Optional[str]] = mapped_column(String(10))
    time_ganji: Mapped[Optional[str]] = mapped_column(String(10))

    is_primary: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )

    # 관계 설정
    user: Mapped["User"] = relationship(
        "User", back_populates="saju_profiles", lazy="selectin"
    )
    daily_fortunes: Mapped[List["DailyFortune"]] = relationship(
        "DailyFortune",
        back_populates="profile",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )
    fortune_logs: Mapped[List["FortuneLog"]] = relationship(
        "FortuneLog",
        back_populates="profile",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )
