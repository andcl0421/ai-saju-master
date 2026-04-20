from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from datetime import date

from openai import AsyncOpenAI

from app.core.saju_engine import GanjiResult

_client: AsyncOpenAI | None = None


@dataclass
class LLMResult:
    summary: str
    advice: str
    luck_item: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: int
    model_name: str

    @property
    def content(self) -> str:
        return f"{self.summary}\n\n{self.advice}".strip()


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _client


def build_fortune_prompt(
    nickname: str,
    ganji: GanjiResult,
    today_ganji: str,
    scores: dict[str, int],
    phrases: dict[str, str],
    target_date: date,
) -> str:
    phrase_context = json.dumps(phrases, ensure_ascii=False)
    time_note = (
        "Birth time is UNKNOWN, so keep hour-pillar interpretation conservative."
        if ganji.is_time_unknown
        else "Birth time is known, so include hour-pillar interpretation."
    )
    return (
        "You are a professional Saju analyst.\n"
        "Return a JSON object only. Do not write any text outside the JSON object.\n"
        "Use this schema exactly:\n"
        "{"
        '"fortune_score": int, '
        '"money_score": int, '
        '"love_score": int, '
        '"health_score": int, '
        '"work_score": int, '
        '"summary": str, '
        '"advice": str, '
        '"luck_item": str'
        "}\n"
        f"Target date: {target_date}\n"
        f"Nickname: {nickname}\n"
        f"Year pillar: {ganji.year_ganji}\n"
        f"Month pillar: {ganji.month_ganji}\n"
        f"Day pillar: {ganji.day_ganji}\n"
        f"Hour pillar: {ganji.time_ganji}\n"
        f"Today's ganji: {today_ganji}\n"
        f"Five elements: {json.dumps(ganji.five_elements, ensure_ascii=False)}\n"
        f"Reference scores: {json.dumps(scores, ensure_ascii=False)}\n"
        f"Reference phrases: {phrase_context}\n"
        f"Constraint: {time_note}\n"
        "Keep the score values identical to the reference scores.\n"
        "Write summary in 2 or 3 sentences.\n"
        "Write advice as a compact paragraph covering money, love, health, and work.\n"
        "luck_item must be a short noun phrase."
    )


def _fallback_result(scores: dict[str, int], phrases: dict[str, str]) -> LLMResult:
    summary = (
        f"Today's overall fortune score is {scores['fortune_score']}. "
        "Staying steady and avoiding rushed decisions will help you use the day well."
    )
    advice = " ".join(
        [
            f"Money {scores['money_score']}: {phrases.get('재물') or 'Watch spending and keep your priorities clear.'}",
            f"Love {scores['love_score']}: {phrases.get('연애') or 'A calm tone will improve communication.'}",
            f"Health {scores['health_score']}: {phrases.get('건강') or 'Protect your energy with rest and regular meals.'}",
            f"Work {scores['work_score']}: {phrases.get('직장') or 'Double-check details before committing.'}",
        ]
    )
    return LLMResult(
        summary=summary,
        advice=advice,
        luck_item="small notebook",
        prompt_tokens=0,
        completion_tokens=0,
        total_tokens=0,
        latency_ms=0,
        model_name="local-fallback",
    )


def _parse_response_content(raw_content: str, scores: dict[str, int]) -> dict[str, str | int]:
    payload = json.loads(raw_content)
    return {
        "fortune_score": int(payload.get("fortune_score", scores["fortune_score"])),
        "money_score": int(payload.get("money_score", scores["money_score"])),
        "love_score": int(payload.get("love_score", scores["love_score"])),
        "health_score": int(payload.get("health_score", scores["health_score"])),
        "work_score": int(payload.get("work_score", scores["work_score"])),
        "summary": str(payload.get("summary", "")).strip(),
        "advice": str(payload.get("advice", "")).strip(),
        "luck_item": str(payload.get("luck_item", "")).strip(),
    }


async def generate_fortune_content(
    prompt: str,
    *,
    scores: dict[str, int],
    phrases: dict[str, str],
    model: str = "gpt-4o",
) -> LLMResult:
    if not os.getenv("OPENAI_API_KEY"):
        return _fallback_result(scores, phrases)

    client = _get_client()
    start = time.monotonic()

    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional Saju analyst. Return JSON only.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            response_format={"type": "json_object"},
        )
        latency_ms = int((time.monotonic() - start) * 1000)
        raw_content = response.choices[0].message.content or "{}"
        parsed = _parse_response_content(raw_content, scores)
        fallback = _fallback_result(scores, phrases)
        usage = response.usage
        return LLMResult(
            summary=str(parsed["summary"]) or fallback.summary,
            advice=str(parsed["advice"]) or fallback.advice,
            luck_item=str(parsed["luck_item"]) or fallback.luck_item,
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
            total_tokens=usage.total_tokens if usage else 0,
            latency_ms=latency_ms,
            model_name=model,
        )
    except Exception:
        return _fallback_result(scores, phrases)
