from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.fortune import (
    FortuneCreateData,
    FortuneCreateRequest,
    FortuneCreateResponse,
    FortuneTodayData,
    FortuneTodayResponse,
    RadarChart,
)
from app.services import fortune_service, saju_service

router = APIRouter(prefix="/api/v1/fortunes", tags=["fortunes"])


def _validate_owner(profile, user_email: str) -> None:
    if profile.user_email != user_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this profile.",
        )


@router.post("", response_model=FortuneCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_daily_fortune(
    body: FortuneCreateRequest,
    db: AsyncSession = Depends(get_db),
) -> FortuneCreateResponse:
    profile = await saju_service.get_profile_by_id(body.profile_id, db)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found.")
    _validate_owner(profile, str(body.user_email))

    fortune = await fortune_service.get_or_create_today_fortune(
        profile,
        db,
        target_date=body.target_date,
    )
    return FortuneCreateResponse(
        status=201,
        message="Daily fortune created successfully.",
        data=FortuneCreateData(
            fortune_id=fortune.fortune_id,
            profile_id=fortune.profile_id,
            created_at=fortune.created_at,
        ),
    )


@router.get("/{profile_id}/today", response_model=FortuneTodayResponse)
async def get_today_fortune(
    profile_id: int,
    user_email: str,
    db: AsyncSession = Depends(get_db),
) -> FortuneTodayResponse:
    profile = await saju_service.get_profile_by_id(profile_id, db)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found.")
    _validate_owner(profile, user_email)

    fortune = await fortune_service.get_or_create_today_fortune(profile, db)
    return FortuneTodayResponse(
        status=200,
        data=FortuneTodayData(
            fortune_id=fortune.fortune_id,
            profile_id=fortune.profile_id,
            target_date=fortune.target_date,
            content=fortune.content,
            summary=fortune.summary,
            advice=fortune.advice,
            luck_item=fortune.luck_item,
            radar_chart=RadarChart(
                money=fortune.money_score,
                love=fortune.love_score,
                health=fortune.health_score,
                work=fortune.work_score,
                total=fortune.fortune_score,
            ),
            status=fortune.status,
            created_at=fortune.created_at,
        ),
    )
