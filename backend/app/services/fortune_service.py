from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import saju_engine
from app.models.fortune import DailyFortune
from app.models.log import FortuneLog
from app.models.saju import SajuProfile
from app.services import llm_service, rag_service


async def get_today_fortune(
    profile_id: int,
    target_date: date,
    db: AsyncSession,
) -> DailyFortune | None:
    result = await db.execute(
        select(DailyFortune).where(
            DailyFortune.profile_id == profile_id,
            DailyFortune.target_date == target_date,
        )
    )
    return result.scalars().first()


async def _create_failure_fortune(
    profile: SajuProfile,
    target_date: date,
    error_message: str,
    db: AsyncSession,
) -> DailyFortune:
    fortune = DailyFortune(
        profile_id=profile.profile_id,
        target_date=target_date,
        fortune_score=0,
        money_score=0,
        love_score=0,
        health_score=0,
        work_score=0,
        content="운세 생성에 실패했습니다.",
        summary="운세 생성에 실패했습니다.",
        advice="잠시 후 다시 시도해 주세요.",
        luck_item=None,
        status="FAIL",
        error_msg=error_message,
    )
    db.add(fortune)
    await db.flush()
    db.add(
        FortuneLog(
            profile_id=profile.profile_id,
            raw_prompt="",
            raw_response=None,
            error_message=error_message,
            target_date=target_date,
            model_name="system",
            status="FAIL",
        )
    )
    await db.commit()
    await db.refresh(fortune)
    return fortune


async def _create_fortune(
    profile: SajuProfile,
    target_date: date,
    db: AsyncSession,
) -> DailyFortune:
    today_ganji = saju_engine.calculate_day_ganji(target_date)
    scores = saju_engine.calculate_scores(
        profile_day_ganji=profile.day_ganji or saju_engine.calculate_day_ganji(profile.birth_date),
        today_ganji=today_ganji,
        seed=int(target_date.strftime("%Y%m%d")) + profile.profile_id,
    )
    fortune_type = saju_engine.get_fortune_type(scores["fortune_score"])
    phrases = await rag_service.get_phrases_for_fortune(fortune_type, db)
    ganji_result = saju_engine.calculate_ganji(profile.birth_date, profile.birth_time)
    prompt = llm_service.build_fortune_prompt(
        nickname=profile.nickname,
        ganji=ganji_result,
        today_ganji=today_ganji,
        scores=scores,
        phrases=phrases,
        target_date=target_date,
    )

    try:
        llm_result = await llm_service.generate_fortune_content(
            prompt,
            scores=scores,
            phrases=phrases,
        )
    except Exception as exc:
        return await _create_failure_fortune(profile, target_date, str(exc), db)

    fortune = DailyFortune(
        profile_id=profile.profile_id,
        target_date=target_date,
        fortune_score=scores["fortune_score"],
        money_score=scores["money_score"],
        love_score=scores["love_score"],
        health_score=scores["health_score"],
        work_score=scores["work_score"],
        content=llm_result.content,
        summary=llm_result.summary,
        advice=llm_result.advice,
        luck_item=llm_result.luck_item or None,
        status="SUCCESS",
    )
    db.add(fortune)

    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        existing = await get_today_fortune(profile.profile_id, target_date, db)
        if existing is None:
            raise
        return existing

    db.add(
        FortuneLog(
            profile_id=profile.profile_id,
            raw_prompt=prompt,
            raw_response=llm_result.content,
            target_date=target_date,
            model_name=llm_result.model_name,
            status=fortune.status,
            latency_ms=llm_result.latency_ms,
            prompt_tokens=llm_result.prompt_tokens,
            completion_tokens=llm_result.completion_tokens,
            total_tokens=llm_result.total_tokens,
        )
    )
    await db.commit()
    await db.refresh(fortune)
    return fortune


async def get_or_create_today_fortune(
    profile: SajuProfile,
    db: AsyncSession,
    *,
    target_date: date | None = None,
) -> DailyFortune:
    today = target_date or datetime.now(timezone.utc).date()
    cached = await get_today_fortune(profile.profile_id, today, db)
    if cached is not None:
        return cached
    return await _create_fortune(profile, today, db)
