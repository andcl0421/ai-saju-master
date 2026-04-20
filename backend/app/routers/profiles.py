from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.profile import (
    MessageResponse,
    PrimaryProfileData,
    PrimaryProfileResponse,
    ProfileCreateData,
    ProfileCreateRequest,
    ProfileCreateResponse,
    ProfileDetail,
    ProfileDetailResponse,
    ProfileListData,
    ProfileListResponse,
    ProfileSummary,
    ProfileUpdateData,
    ProfileUpdateRequest,
    ProfileUpdateResponse,
)
from app.services import saju_service

router = APIRouter(prefix="/api/v1/profiles", tags=["profiles"])


def _to_profile_detail(profile) -> ProfileDetail:
    return ProfileDetail(
        profile_id=profile.profile_id,
        user_email=profile.user_email,
        nickname=profile.nickname,
        birth_date=profile.birth_date,
        birth_time=profile.birth_time,
        gender=profile.gender.value,
        calendar_type=profile.calendar_type.value,
        year_ganji=profile.year_ganji,
        month_ganji=profile.month_ganji,
        day_ganji=profile.day_ganji,
        time_ganji=profile.time_ganji,
        is_primary=profile.is_primary,
        is_time_unknown=(profile.birth_time == "UNKNOWN"),
        created_at=profile.created_at,
    )


@router.post("", response_model=ProfileCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    body: ProfileCreateRequest,
    db: AsyncSession = Depends(get_db),
) -> ProfileCreateResponse:
    try:
        profile = await saju_service.create_profile(body, db)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return ProfileCreateResponse(
        status=201,
        data=ProfileCreateData(profile_id=profile.profile_id, nickname=profile.nickname),
    )


@router.get("", response_model=ProfileListResponse)
async def get_profiles(
    user_email: str = Query(...),
    db: AsyncSession = Depends(get_db),
) -> ProfileListResponse:
    profiles = await saju_service.list_profiles(user_email, db)
    return ProfileListResponse(
        status=200,
        data=ProfileListData(
            user_email=user_email,
            profiles=[
                ProfileSummary(
                    profile_id=profile.profile_id,
                    nickname=profile.nickname,
                    is_primary=profile.is_primary,
                )
                for profile in profiles
            ],
        ),
    )


@router.get("/{profile_id}", response_model=ProfileDetailResponse)
async def get_profile_detail(
    profile_id: int,
    db: AsyncSession = Depends(get_db),
) -> ProfileDetailResponse:
    profile = await saju_service.get_profile_by_id(profile_id, db)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found.")
    return ProfileDetailResponse(status=200, data=_to_profile_detail(profile))


@router.patch("/{profile_id}", response_model=ProfileUpdateResponse)
async def update_profile(
    profile_id: int,
    body: ProfileUpdateRequest,
    db: AsyncSession = Depends(get_db),
) -> ProfileUpdateResponse:
    profile, updated_fields = await saju_service.update_profile(profile_id, body, db)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found.")

    return ProfileUpdateResponse(
        status=200,
        message="Profile updated successfully.",
        data=ProfileUpdateData(profile_id=profile.profile_id, updated_fields=updated_fields),
    )


@router.patch("/{profile_id}/primary", response_model=PrimaryProfileResponse)
async def set_primary_profile(
    profile_id: int,
    db: AsyncSession = Depends(get_db),
) -> PrimaryProfileResponse:
    profile = await saju_service.set_primary_profile(profile_id, db)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found.")

    return PrimaryProfileResponse(
        status=200,
        message="Primary profile updated successfully.",
        data=PrimaryProfileData(
            user_email=profile.user_email,
            primary_profile_id=profile.profile_id,
            is_primary=profile.is_primary,
        ),
    )


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    profile_id: int,
    reason: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> Response:
    deleted = await saju_service.delete_profile(profile_id, db)
    if not deleted:
        raise HTTPException(status_code=404, detail="Profile not found.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
