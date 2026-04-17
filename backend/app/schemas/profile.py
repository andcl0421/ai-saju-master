"""
schemas/profile.py
POST /profiles 요청/응답 스키마
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ProfileCreate(BaseModel):
    """POST /profiles 요청 바디"""

    email: EmailStr
    nickname: str = Field(..., min_length=1, max_length=50)
    birth_date: date
    birth_time: str = Field(
        default="UNKNOWN",
        description="HH:MM 형식 또는 'UNKNOWN'",
        pattern=r"^(\d{2}:\d{2}|UNKNOWN)$",
    )
    gender: Literal["MALE", "FEMALE"]
    calendar_type: Literal["SOLAR", "LUNAR"] = "SOLAR"
    is_primary: bool = False


class ProfileResponse(BaseModel):
    """POST /profiles 응답"""

    model_config = ConfigDict(from_attributes=True)

    profile_id: int
    user_email: str
    nickname: str
    birth_date: date
    birth_time: str
    gender: str
    calendar_type: Optional[str] = None
    year_ganji: Optional[str] = None
    month_ganji: Optional[str] = None
    day_ganji: Optional[str] = None
    time_ganji: Optional[str] = None
    is_primary: bool
    is_time_unknown: bool = Field(
        default=False,
        description="생시 미입력 여부 (프론트 안내 문구 표시용)",
    )
    created_at: datetime
