"""
services/saju_service.py

사용자(users) Silent Upsert 및 사주 프로필(saju_profiles) 생성/재사용.

규칙:
- DB 접근은 이 서비스에서만 수행
- 간지 계산은 core/saju_engine.py 에 위임
- PostgreSQL ON CONFLICT DO UPDATE (Upsert) 사용
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.saju_engine import GanjiResult, calculate_ganji
from app.models.saju import SajuProfile
from app.models.user import User
from app.schemas.profile import ProfileCreate


# ─────────────────────────────────────────────
# Users — Silent Upsert
# ─────────────────────────────────────────────
async def upsert_user(email: str, db: AsyncSession) -> User:
    """
    이메일로 사용자를 조회하고, 없으면 생성합니다 (Silent Upsert).
    ON CONFLICT(email) DO UPDATE last_login 방식으로 단일 쿼리 처리.
    """
    stmt = (
        pg_insert(User)
        .values(email=email)
        .on_conflict_do_update(
            index_elements=["email"],
            set_={"last_login": datetime.now(timezone.utc)},
        )
        .returning(User)
    )
    result = await db.execute(stmt)
    await db.commit()

    # returning 으로 받은 행을 ORM 객체로 변환
    row = result.fetchone()
    if row is None:
        # 혹시 returning 이 비어있는 경우 명시적 조회
        user_result = await db.execute(select(User).where(User.email == email))
        return user_result.scalars().one()

    return row[0]


# ─────────────────────────────────────────────
# SajuProfile — 조회 or 생성 (캐싱)
# ─────────────────────────────────────────────
async def _find_existing_profile(
    email: str,
    nickname: str,
    birth_date,
    db: AsyncSession,
) -> Optional[SajuProfile]:
    """
    (email, nickname, birth_date) 동일 조합 프로필 조회.
    같은 프로필을 중복 생성하지 않기 위한 캐싱 조회.
    """
    result = await db.execute(
        select(SajuProfile).where(
            SajuProfile.user_email == email,
            SajuProfile.nickname == nickname,
            SajuProfile.birth_date == birth_date,
        )
    )
    return result.scalars().first()


def _needs_ganji_recalc(profile: SajuProfile) -> bool:
    """간지 캐싱이 빠져있으면 재계산 필요"""
    return not all([
        profile.year_ganji,
        profile.month_ganji,
        profile.day_ganji,
        profile.time_ganji,
    ])


async def _apply_ganji(
    profile: SajuProfile,
    ganji: GanjiResult,
    db: AsyncSession,
) -> SajuProfile:
    """간지 결과를 프로필에 저장"""
    profile.year_ganji = ganji.year_ganji
    profile.month_ganji = ganji.month_ganji
    profile.day_ganji = ganji.day_ganji
    profile.time_ganji = ganji.time_ganji
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile


async def get_or_create_profile(
    data: ProfileCreate,
    db: AsyncSession,
) -> tuple[SajuProfile, bool]:
    """
    프로필을 조회하거나 새로 생성합니다.

    1. users 테이블 Upsert
    2. 동일 (email, nickname, birth_date) 프로필 탐색
       - 존재하면: 간지 캐싱 여부 확인 → 없으면 재계산 후 저장
       - 없으면: 간지 계산 후 신규 생성
    3. (profile, is_created: bool) 반환

    Returns
    -------
    (SajuProfile, is_created)
    """
    await upsert_user(data.email, db)

    existing = await _find_existing_profile(
        data.email, data.nickname, data.birth_date, db
    )

    if existing:
        if _needs_ganji_recalc(existing):
            ganji = calculate_ganji(existing.birth_date, existing.birth_time)
            existing = await _apply_ganji(existing, ganji, db)
        return existing, False

    # 신규 생성
    ganji = calculate_ganji(data.birth_date, data.birth_time)

    profile = SajuProfile(
        user_email=data.email,
        nickname=data.nickname,
        birth_date=data.birth_date,
        birth_time=data.birth_time,
        gender=data.gender,
        year_ganji=ganji.year_ganji,
        month_ganji=ganji.month_ganji,
        day_ganji=ganji.day_ganji,
        time_ganji=ganji.time_ganji,
        is_primary=data.is_primary,
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile, True


async def get_profile_by_id(
    profile_id: int,
    db: AsyncSession,
) -> Optional[SajuProfile]:
    """profile_id 로 프로필 단건 조회"""
    result = await db.execute(
        select(SajuProfile).where(SajuProfile.profile_id == profile_id)
    )
    return result.scalars().first()


async def get_primary_profile(
    email: str,
    db: AsyncSession,
) -> Optional[SajuProfile]:
    """이메일 기준 is_primary=True 프로필 조회"""
    result = await db.execute(
        select(SajuProfile).where(
            SajuProfile.user_email == email,
            SajuProfile.is_primary.is_(True),
        )
    )
    return result.scalars().first()
