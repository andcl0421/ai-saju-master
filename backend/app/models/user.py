from __future__ import annotations
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import (
    String,
    DateTime,
    Boolean,
    ForeignKey,
    Index,
    func,
    text,
    BigInteger,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base

if TYPE_CHECKING:
    from app.models.saju import SajuProfile


class User(Base):
    """사용자 계정 정보"""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(100), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # 관계 설정
    saju_profiles: Mapped[List["SajuProfile"]] = relationship(
        "SajuProfile",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )
    push_subscriptions: Mapped[List["PushSubscription"]] = relationship(
        "PushSubscription",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )


class PushSubscription(Base):
    """FCM 푸시 알림 구독 정보"""

    __tablename__ = "push_subscriptions"
    __table_args__ = (Index("idx_push_email", "user_email"),)

    sub_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    user_email: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("users.email", ondelete="CASCADE"),
        nullable=False,
    )
    fcm_token: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        "User", back_populates="push_subscriptions", lazy="selectin"
    )
