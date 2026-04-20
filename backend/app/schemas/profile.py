from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ProfileCreateRequest(BaseModel):
    user_email: EmailStr
    nickname: str = Field(..., min_length=1, max_length=50)
    birth_date: date
    birth_time: str = Field(default="UNKNOWN", pattern=r"^(\d{2}:\d{2}|UNKNOWN)$")
    gender: Literal["MALE", "FEMALE"]
    calendar_type: Literal["SOLAR", "LUNAR"] = "SOLAR"
    is_primary: bool = False


class ProfileUpdateRequest(BaseModel):
    nickname: str | None = Field(default=None, min_length=1, max_length=50)
    birth_date: date | None = None
    birth_time: str | None = Field(default=None, pattern=r"^(\d{2}:\d{2}|UNKNOWN)$")
    gender: Literal["MALE", "FEMALE"] | None = None
    calendar_type: Literal["SOLAR", "LUNAR"] | None = None


class ProfileSummary(BaseModel):
    profile_id: int
    nickname: str
    is_primary: bool


class ProfileDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    profile_id: int
    user_email: str
    nickname: str
    birth_date: date
    birth_time: str
    gender: str
    calendar_type: str
    year_ganji: str | None = None
    month_ganji: str | None = None
    day_ganji: str | None = None
    time_ganji: str | None = None
    is_primary: bool
    is_time_unknown: bool
    created_at: datetime


class ProfileCreateData(BaseModel):
    profile_id: int
    nickname: str


class ProfileCreateResponse(BaseModel):
    status: int
    data: ProfileCreateData


class ProfileListData(BaseModel):
    user_email: str
    profiles: list[ProfileSummary]


class ProfileListResponse(BaseModel):
    status: int
    data: ProfileListData


class ProfileDetailResponse(BaseModel):
    status: int
    data: ProfileDetail


class ProfileUpdateData(BaseModel):
    profile_id: int
    updated_fields: list[str]


class ProfileUpdateResponse(BaseModel):
    status: int
    message: str
    data: ProfileUpdateData


class PrimaryProfileData(BaseModel):
    user_email: str
    primary_profile_id: int
    is_primary: bool


class PrimaryProfileResponse(BaseModel):
    status: int
    message: str
    data: PrimaryProfileData


class MessageResponse(BaseModel):
    status: int
    message: str
