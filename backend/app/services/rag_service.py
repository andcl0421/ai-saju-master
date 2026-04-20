from __future__ import annotations

from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fortune import FortunePhrase


async def get_random_phrase(
    category: str,
    mood: str,
    db: AsyncSession,
) -> Optional[FortunePhrase]:
    result = await db.execute(
        select(FortunePhrase)
        .where(
            FortunePhrase.category == category,
            FortunePhrase.mood == mood,
        )
        .order_by(func.random())
        .limit(1)
    )
    phrase = result.scalars().first()
    if phrase is not None:
        return phrase

    fallback = await db.execute(
        select(FortunePhrase)
        .where(FortunePhrase.category == category)
        .order_by(func.random())
        .limit(1)
    )
    return fallback.scalars().first()


async def get_phrases_for_fortune(
    fortune_type: str,
    db: AsyncSession,
) -> dict[str, str]:
    mood = fortune_type if fortune_type in {"GOOD", "NORMAL", "BAD"} else "BAD"
    categories = ["재물", "연애", "건강", "직장"]
    phrases: dict[str, str] = {}

    for category in categories:
        phrase = await get_random_phrase(category, mood, db)
        phrases[category] = phrase.content if phrase else ""

    return phrases
