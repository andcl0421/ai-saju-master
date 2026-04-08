from __future__ import annotations
from datetime import date, datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import ForeignKey, Text, Date, DateTime, BigInteger, func, String, Integer , UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base


if TYPE_CHECKING:
    from app.models.saju import SajuProfile
    
class FortuneLog(Base):
    """AI 운세 생성 프롬프트 및 응답 로그 (비용/성능 지표 보완)"""

    __tablename__ = "fortune_logs"

    log_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("saju_profiles.profile_id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # [보완] 어떤 모델을 썼고, 성공했는지 기록
    model_name: Mapped[str] = mapped_column(String(50), server_default="gpt-4o")
    status: Mapped[str] = mapped_column(String(10), server_default="SUCCESS") 

    # 데이터 원문 (Optional을 빼고 nullable=False로 관리하는 것이 운영상 유리합니다)
    raw_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    raw_response: Mapped[Optional[str]] = mapped_column(Text)
    error_message: Mapped[Optional[str]] = mapped_column(Text) # 실패 시 사유

    # [보완] 명세서에 있는 성능/비용 지표들
    latency_ms: Mapped[int] = mapped_column(Integer, server_default="0")
    prompt_tokens: Mapped[int] = mapped_column(Integer, server_default="0")
    completion_tokens: Mapped[int] = mapped_column(Integer, server_default="0")
    total_tokens: Mapped[int] = mapped_column(Integer, server_default="0")

    target_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    profile: Mapped["SajuProfile"] = relationship(
        "SajuProfile", back_populates="fortune_logs", lazy="selectin"
    )