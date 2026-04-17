"""
routers/fortune.py

GET /fortune/today
- 요청 파싱 및 응답 직렬화만 담당
- DB 접근 금지 — 모든 로직은 fortune_service / saju_service 에 위임
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.saju_engine import get_fortune_type
from app.db.database import get_db
from app.schemas.fortune import FortuneResponse
from app.services import fortune_service, saju_service

router = APIRouter(prefix="/fortune", tags=["fortune"])


@router.get(
    "/today",
    response_model=FortuneResponse,
    summary="오늘의 운세 조회",
    description=(
        "profile_id 기준 오늘 운세를 반환합니다.\n\n"
        "DB에 오늘 운세가 없으면 자동 생성 후 반환합니다 (캐싱 구조).\n\n"
        "email 은 프로필 소유자 검증에 사용됩니다."
    ),
)
async def get_today_fortune(
    email: EmailStr = Query(..., description="사용자 이메일"),
    profile_id: int = Query(..., description="운세를 조회할 사주 프로필 ID"),
    db: AsyncSession = Depends(get_db),
) -> FortuneResponse:
    # 프로필 조회 (서비스 위임)
    profile = await saju_service.get_profile_by_id(profile_id, db)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "PROFILE_NOT_FOUND", "message": "프로필을 찾을 수 없습니다."},
        )

    # 이메일 소유권 검증
    if profile.user_email != str(email):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": "해당 프로필에 접근 권한이 없습니다."},
        )

    # 운세 조회 or 생성 (서비스 위임)
    fortune = await fortune_service.get_or_create_today_fortune(profile, db)

    return FortuneResponse(
        fortune_id=fortune.fortune_id,
        profile_id=fortune.profile_id,
        target_date=fortune.target_date,
        fortune_score=fortune.fortune_score,
        money_score=fortune.money_score,
        love_score=fortune.love_score,
        health_score=fortune.health_score,
        work_score=fortune.work_score,
        fortune_type=get_fortune_type(fortune.fortune_score),
        content=fortune.content,
        luck_item=fortune.luck_item,
        is_time_unknown=(profile.birth_time == "UNKNOWN"),
        created_at=fortune.created_at,
    )
