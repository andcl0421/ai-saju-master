"""
services/rag_service.py

fortune_phrases 테이블에서 운세 문구 조회.
RAG(Vector DB) 사용 금지 — DB 직접 조회만 허용 (커서.md 규칙).
"""
from __future__ import annotations

import random
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fortune import FortunePhrase


async def get_phrases_by_mood(
    category: str,
    mood: str,
    db: AsyncSession,
) -> list[FortunePhrase]:
    """
    카테고리 + 기분(mood)으로 운세 문구 목록 조회.

    Parameters
    ----------
    category : "재물" | "연애" | "건강" | "직장" 등 fortune_phrases.category 값
    mood     : "GOOD" | "NORMAL" | "BAD" | "VERY_BAD"
    """
    result = await db.execute(
        select(FortunePhrase).where(
            FortunePhrase.category == category,
            FortunePhrase.mood == mood,
        )
    )
    return list(result.scalars().all())


async def get_random_phrase(
    category: str,
    mood: str,
    db: AsyncSession,
) -> Optional[FortunePhrase]:
    """
    카테고리 + mood 조건에서 DB ORDER BY RANDOM() 으로 1건 조회.
    해당 조건 문구가 없으면 mood 조건 완화 후 재조회, 그래도 없으면 None 반환.
    """
    stmt = (
        select(FortunePhrase)
        .where(
            FortunePhrase.category == category,
            FortunePhrase.mood == mood,
        )
        .order_by(func.random())
        .limit(1)
    )
    result = await db.execute(stmt)
    phrase = result.scalars().first()

    if phrase is None:
        # mood 조건 완화 — 같은 카테고리에서 아무거나
        fallback_stmt = (
            select(FortunePhrase)
            .where(FortunePhrase.category == category)
            .order_by(func.random())
            .limit(1)
        )
        fallback_result = await db.execute(fallback_stmt)
        phrase = fallback_result.scalars().first()

    return phrase


async def get_phrases_for_fortune(
    fortune_type: str,
    db: AsyncSession,
) -> dict[str, str]:
    """
    운세 유형(GOOD/NORMAL/BAD/VERY_BAD)에 맞는 카테고리별 대표 문구 반환.

    Returns
    -------
    {
        "재물": "...",
        "연애": "...",
        "건강": "...",
        "직장": "...",
    }
    mood 매핑: VERY_BAD → BAD 로 폴백
    """
    mood = fortune_type if fortune_type in ("GOOD", "NORMAL", "BAD") else "BAD"

    categories = ["재물", "연애", "건강", "직장"]
    results: dict[str, str] = {}

    for category in categories:
        phrase = await get_random_phrase(category, mood, db)
        results[category] = phrase.content if phrase else ""

    return results
