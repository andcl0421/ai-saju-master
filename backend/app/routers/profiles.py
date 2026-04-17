"""
routers/profiles.py

POST /profiles
- 요청 파싱 및 응답 직렬화만 담당
- DB 접근 금지 — 모든 로직은 saju_service 에 위임
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.profile import ProfileCreate, ProfileResponse
from app.services import saju_service

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.post(
    "",
    response_model=ProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="사주 프로필 생성",
    description=(
        "이메일 기반 Silent Upsert + 사주 프로필 생성.\n\n"
        "동일 (email, nickname, birth_date) 조합이 이미 존재하면 기존 프로필을 반환합니다."
    ),
)
async def create_profile(
    body: ProfileCreate,
    db: AsyncSession = Depends(get_db),
) -> ProfileResponse:
    profile, _ = await saju_service.get_or_create_profile(body, db)

    return ProfileResponse(
        profile_id=profile.profile_id,
        user_email=profile.user_email,
        nickname=profile.nickname,
        birth_date=profile.birth_date,
        birth_time=profile.birth_time,
        gender=profile.gender,
        year_ganji=profile.year_ganji,
        month_ganji=profile.month_ganji,
        day_ganji=profile.day_ganji,
        time_ganji=profile.time_ganji,
        is_primary=profile.is_primary,
        is_time_unknown=(profile.birth_time == "UNKNOWN"),
        created_at=profile.created_at,
    )
