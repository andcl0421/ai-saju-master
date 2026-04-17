"""
services/fortune_service.py

오늘의 운세 조회/생성 서비스.

흐름:
  1. DB 캐싱 조회 (profile_id + target_date UNIQUE)
  2. 없으면 Score Engine 실행
  3. fortune_phrases 조회 (rag_service)
  4. LLM 문장 생성 (llm_service)
  5. DailyFortune + FortuneLog 저장
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import saju_engine
from app.models.fortune import DailyFortune
from app.models.log import FortuneLog
from app.models.saju import SajuProfile
from app.services import llm_service, rag_service


# ─────────────────────────────────────────────
# 캐싱 조회
# ─────────────────────────────────────────────
async def get_today_fortune(
    profile_id: int,
    target_date: date,
    db: AsyncSession,
) -> Optional[DailyFortune]:
    """
    DB에서 오늘 운세를 조회합니다.
    UNIQUE(profile_id, target_date) 제약 기반 단건 조회.
    """
    result = await db.execute(
        select(DailyFortune).where(
            DailyFortune.profile_id == profile_id,
            DailyFortune.target_date == target_date,
        )
    )
    return result.scalars().first()


# ─────────────────────────────────────────────
# 운세 생성
# ─────────────────────────────────────────────
async def _create_fortune(
    profile: SajuProfile,
    target_date: date,
    db: AsyncSession,
) -> DailyFortune:
    """
    Score Engine → Phrase 조회 → LLM 생성 → DB 저장 → Log 저장.
    LLM 실패 시 status='FAIL' 로 기록하고 예외를 다시 올립니다.
    """
    # 1. 오늘 일진 계산
    today_ganji = saju_engine.calculate_day_ganji(target_date)

    # 2. Score Engine
    scores = saju_engine.calculate_scores(
        profile_day_ganji=profile.day_ganji or saju_engine.calculate_day_ganji(profile.birth_date),
        today_ganji=today_ganji,
        seed=int(target_date.strftime("%Y%m%d")) + profile.profile_id,
    )
    fortune_type = saju_engine.get_fortune_type(scores["fortune_score"])

    # 3. fortune_phrases 조회
    phrases = await rag_service.get_phrases_for_fortune(fortune_type, db)

    # 4. 프로필 간지 복원 (캐싱 없을 경우 재계산)
    birth_time = profile.birth_time or "UNKNOWN"
    ganji_result = saju_engine.GanjiResult(
        year_ganji=profile.year_ganji or "",
        month_ganji=profile.month_ganji or "",
        day_ganji=profile.day_ganji or "",
        time_ganji=profile.time_ganji or "",
        five_elements=saju_engine.calculate_five_elements(
            profile.year_ganji or "",
            profile.month_ganji or "",
            profile.day_ganji or "",
            profile.time_ganji or "",
        ),
        calculated_birth_time="12:00" if birth_time == "UNKNOWN" else birth_time,
        is_time_unknown=(birth_time == "UNKNOWN"),
    )

    # 5. LLM 프롬프트 생성 및 호출
    prompt = llm_service.build_fortune_prompt(
        nickname=profile.nickname,
        ganji=ganji_result,
        today_ganji=today_ganji,
        scores=scores,
        phrases=phrases,
        target_date=target_date,
    )

    llm_result = await llm_service.generate_fortune_content(prompt)

    # 6. DailyFortune 저장
    fortune = DailyFortune(
        profile_id=profile.profile_id,
        target_date=target_date,
        fortune_score=scores["fortune_score"],
        money_score=scores["money_score"],
        love_score=scores["love_score"],
        health_score=scores["health_score"],
        work_score=scores["work_score"],
        content=llm_result.content,
        luck_item=llm_result.luck_item or None,
        status="SUCCESS",
    )
    db.add(fortune)

    try:
        await db.flush()   # PK 획득 (commit 전 ID 필요)
    except IntegrityError:
        # 동시 요청으로 인한 UNIQUE 충돌 → 이미 생성된 운세 반환
        await db.rollback()
        return await get_today_fortune(profile.profile_id, target_date, db)  # type: ignore[return-value]

    # 7. FortuneLog 저장
    log = FortuneLog(
        profile_id=profile.profile_id,
        raw_prompt=prompt,
        raw_response=llm_result.content,
        target_date=target_date,
        model_name=llm_result.model_name,
        status="SUCCESS",
        latency_ms=llm_result.latency_ms,
        prompt_tokens=llm_result.prompt_tokens,
        completion_tokens=llm_result.completion_tokens,
        total_tokens=llm_result.total_tokens,
    )
    db.add(log)
    await db.commit()
    await db.refresh(fortune)
    return fortune


# ─────────────────────────────────────────────
# 진입점 (캐싱 + 생성 통합)
# ─────────────────────────────────────────────
async def get_or_create_today_fortune(
    profile: SajuProfile,
    db: AsyncSession,
    *,
    target_date: Optional[date] = None,
) -> DailyFortune:
    """
    오늘 운세 캐싱 진입점.

    - DB에 오늘 운세가 있으면 그대로 반환
    - 없으면 생성 후 반환
    """
    today = target_date or datetime.now(timezone.utc).date()

    cached = await get_today_fortune(profile.profile_id, today, db)
    if cached:
        return cached

    return await _create_fortune(profile, today, db)
