from __future__ import annotations
from datetime import date, datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import ForeignKey, Text, Date, DateTime, BigInteger, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base


if TYPE_CHECKING:
    from app.models.saju import SajuProfile
    
class FortuneLog(Base):
    """AI 운세 생성 프롬프트 및 응답 로그"""

    __tablename__ = "fortune_logs"

    log_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    profile_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("saju_profiles.profile_id", ondelete="CASCADE"),
        nullable=False,
    )
    prompt: Mapped[Optional[str]] = mapped_column(Text)
    response: Mapped[Optional[str]] = mapped_column(Text)
    target_date: Mapped[Optional[date]] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    profile: Mapped["SajuProfile"] = relationship(
        "SajuProfile", back_populates="fortune_logs", lazy="selectin"
    )
