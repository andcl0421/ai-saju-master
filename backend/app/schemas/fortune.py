"""
schemas/fortune.py
GET /fortune/today 응답 스키마
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class FortuneResponse(BaseModel):
    """GET /fortune/today 응답"""

    model_config = ConfigDict(from_attributes=True)

    fortune_id: int
    profile_id: int
    target_date: date
    fortune_score: int = Field(..., ge=0, le=100)
    money_score: int = Field(..., ge=0, le=100)
    love_score: int = Field(..., ge=0, le=100)
    health_score: int = Field(..., ge=0, le=100)
    work_score: int = Field(..., ge=0, le=100)
    fortune_type: str = Field(
        description="GOOD / NORMAL / BAD / VERY_BAD"
    )
    content: str
    luck_item: Optional[str] = None
    is_time_unknown: bool = Field(
        default=False,
        description="생시 미입력 여부 — True 이면 프론트에서 안내 문구 표시",
    )
    created_at: datetime
