from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field


class FortuneCreateRequest(BaseModel):
    profile_id: int
    user_email: EmailStr
    target_date: date | None = None


class FortuneCreateData(BaseModel):
    fortune_id: int
    profile_id: int
    created_at: datetime


class FortuneCreateResponse(BaseModel):
    status: int
    message: str
    data: FortuneCreateData


class RadarChart(BaseModel):
    money: int = Field(..., ge=0, le=100)
    love: int = Field(..., ge=0, le=100)
    health: int = Field(..., ge=0, le=100)
    work: int = Field(..., ge=0, le=100)
    total: int = Field(..., ge=0, le=100)


class FortuneTodayData(BaseModel):
    fortune_id: int
    profile_id: int
    target_date: date
    content: str
    summary: str
    advice: str
    luck_item: str | None = None
    radar_chart: RadarChart
    status: str
    created_at: datetime


class FortuneTodayResponse(BaseModel):
    status: int
    data: FortuneTodayData
