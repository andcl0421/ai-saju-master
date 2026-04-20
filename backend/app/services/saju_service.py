from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.saju_engine import calculate_ganji
from app.models.saju import CalendarType, Gender, SajuProfile
from app.models.user import User
from app.schemas.profile import ProfileCreateRequest, ProfileUpdateRequest

MAX_PROFILES_PER_USER = 5


async def upsert_user(email: str, db: AsyncSession) -> User:
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
    row = result.fetchone()
    await db.commit()

    if row is not None:
        return row[0]

    fallback = await db.execute(select(User).where(User.email == email))
    return fallback.scalars().one()


async def _profile_count(user_email: str, db: AsyncSession) -> int:
    result = await db.execute(
        select(func.count()).select_from(SajuProfile).where(SajuProfile.user_email == user_email)
    )
    return int(result.scalar_one())


async def _recalculate_ganji(profile: SajuProfile, db: AsyncSession) -> SajuProfile:
    ganji = calculate_ganji(profile.birth_date, profile.birth_time)
    profile.year_ganji = ganji.year_ganji
    profile.month_ganji = ganji.month_ganji
    profile.day_ganji = ganji.day_ganji
    profile.time_ganji = ganji.time_ganji
    db.add(profile)
    await db.flush()
    return profile


async def _set_primary_profile(profile: SajuProfile, db: AsyncSession) -> None:
    await db.execute(
        update(SajuProfile)
        .where(
            SajuProfile.user_email == profile.user_email,
            SajuProfile.profile_id != profile.profile_id,
        )
        .values(is_primary=False)
    )
    profile.is_primary = True
    db.add(profile)


async def create_profile(
    data: ProfileCreateRequest,
    db: AsyncSession,
) -> SajuProfile:
    await upsert_user(str(data.user_email), db)

    if await _profile_count(str(data.user_email), db) >= MAX_PROFILES_PER_USER:
        raise ValueError("A user can own up to 5 profiles.")

    ganji = calculate_ganji(data.birth_date, data.birth_time)
    profile = SajuProfile(
        user_email=str(data.user_email),
        nickname=data.nickname,
        birth_date=data.birth_date,
        birth_time=data.birth_time,
        gender=Gender(data.gender),
        calendar_type=CalendarType(data.calendar_type),
        year_ganji=ganji.year_ganji,
        month_ganji=ganji.month_ganji,
        day_ganji=ganji.day_ganji,
        time_ganji=ganji.time_ganji,
        is_primary=data.is_primary,
    )
    db.add(profile)
    await db.flush()

    if data.is_primary or await _profile_count(str(data.user_email), db) == 1:
        await _set_primary_profile(profile, db)

    await db.commit()
    await db.refresh(profile)
    return profile


async def list_profiles(user_email: str, db: AsyncSession) -> list[SajuProfile]:
    result = await db.execute(
        select(SajuProfile)
        .where(SajuProfile.user_email == user_email)
        .order_by(SajuProfile.is_primary.desc(), SajuProfile.created_at.asc())
    )
    return list(result.scalars().all())


async def get_profile_by_id(profile_id: int, db: AsyncSession) -> SajuProfile | None:
    result = await db.execute(select(SajuProfile).where(SajuProfile.profile_id == profile_id))
    return result.scalars().first()


async def update_profile(
    profile_id: int,
    payload: ProfileUpdateRequest,
    db: AsyncSession,
) -> tuple[SajuProfile | None, list[str]]:
    profile = await get_profile_by_id(profile_id, db)
    if profile is None:
        return None, []

    updated_fields: list[str] = []
    recalc_required = False
    for field in ("nickname", "birth_date", "birth_time", "gender", "calendar_type"):
        value = getattr(payload, field)
        if value is None:
            continue
        if field == "gender":
            value = Gender(value)
        if field == "calendar_type":
            value = CalendarType(value)
        setattr(profile, field, value)
        updated_fields.append(field)
        if field in {"birth_date", "birth_time", "calendar_type"}:
            recalc_required = True

    if recalc_required:
        await _recalculate_ganji(profile, db)

    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile, updated_fields


async def set_primary_profile(
    profile_id: int,
    db: AsyncSession,
) -> SajuProfile | None:
    profile = await get_profile_by_id(profile_id, db)
    if profile is None:
        return None

    await _set_primary_profile(profile, db)
    await db.commit()
    await db.refresh(profile)
    return profile


async def delete_profile(profile_id: int, db: AsyncSession) -> bool:
    profile = await get_profile_by_id(profile_id, db)
    if profile is None:
        return False

    user_email = profile.user_email
    was_primary = profile.is_primary
    await db.delete(profile)
    await db.flush()

    if was_primary:
        remaining = await db.execute(
            select(SajuProfile)
            .where(SajuProfile.user_email == user_email)
            .order_by(SajuProfile.created_at.asc())
            .limit(1)
        )
        next_profile = remaining.scalars().first()
        if next_profile is not None:
            next_profile.is_primary = True
            db.add(next_profile)

    await db.commit()
    return True
