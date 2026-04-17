"""
services/llm_service.py

OpenAI AsyncOpenAI 클라이언트를 통한 운세 문장 생성.
openai >= 2.30.0 기준.
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass
from datetime import date
from typing import Optional

from openai import AsyncOpenAI

from app.core.saju_engine import GanjiResult, get_fortune_type

_client: Optional[AsyncOpenAI] = None


def _get_client() -> AsyncOpenAI:
    """AsyncOpenAI 싱글턴 클라이언트"""
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _client


# ─────────────────────────────────────────────
# 데이터클래스
# ─────────────────────────────────────────────
@dataclass
class LLMResult:
    content: str
    luck_item: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: int
    model_name: str


# ─────────────────────────────────────────────
# 프롬프트 빌더
# ─────────────────────────────────────────────
def build_fortune_prompt(
    nickname: str,
    ganji: GanjiResult,
    today_ganji: str,
    scores: dict[str, int],
    phrases: dict[str, str],
    target_date: date,
) -> str:
    """
    LLM에게 전달할 운세 생성 프롬프트를 조립합니다.

    - birth_time 이 UNKNOWN 인 경우 삼주(연·월·일) 중심 해석 안내를 포함.
    - fortune_phrases 템플릿을 컨텍스트로 주입하여 LLM 토큰 비용을 절감.
    """
    fortune_type = get_fortune_type(scores["fortune_score"])
    time_unknown_notice = (
        "\n※ 태어난 시간을 모르시는 경우의 해석입니다. 시주(時柱) 해석은 제외하고 연·월·일 중심으로 설명해주세요.\n"
        if ganji.is_time_unknown
        else ""
    )

    phrase_context = "\n".join(
        f"[{cat}] {text}" for cat, text in phrases.items() if text
    )

    return f"""당신은 전문 명리학 선생님입니다. 아래 사주 정보를 바탕으로 오늘의 운세를 자연스럽고 따뜻하게 작성해주세요.
{time_unknown_notice}
## 기본 정보
- 이름(별명): {nickname}
- 운세 날짜: {target_date}
- 사주 간지: 연({ganji.year_ganji}) 월({ganji.month_ganji}) 일({ganji.day_ganji}) 시({ganji.time_ganji})
- 오늘 일진: {today_ganji}
- 오행 분포: {ganji.five_elements}

## 운세 점수
- 종합: {scores["fortune_score"]}점 ({fortune_type})
- 재물: {scores["money_score"]}점
- 연애: {scores["love_score"]}점
- 건강: {scores["health_score"]}점
- 직장/학업: {scores["work_score"]}점

## 참고 문구 템플릿
{phrase_context}

## 작성 지침
1. 300~400자 분량으로 오늘의 종합 운세를 작성하세요.
2. 재물운, 연애운, 건강운, 직장운을 각 1~2문장으로 포함하세요.
3. 마지막 줄에 오늘의 행운 아이템을 "행운 아이템: XXX" 형식으로 작성하세요.
4. 긍정적이고 실용적인 조언 중심으로 작성하세요.
5. 점수 숫자나 운세 유형 코드(GOOD 등)를 직접 노출하지 마세요."""


# ─────────────────────────────────────────────
# LLM 호출
# ─────────────────────────────────────────────
async def generate_fortune_content(
    prompt: str,
    model: str = "gpt-4o-mini",
) -> LLMResult:
    """
    OpenAI Chat Completions API 호출 후 LLMResult 반환.

    Parameters
    ----------
    prompt : build_fortune_prompt() 로 생성된 프롬프트 문자열
    model  : 사용할 모델명 (기본값: gpt-4o-mini, 비용 절감)
    """
    client = _get_client()
    start = time.monotonic()

    response = await client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "당신은 한국 전통 명리학에 정통한 전문가입니다. "
                    "사주 팔자 데이터를 기반으로 정확하고 따뜻한 운세 해석을 제공합니다."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=600,
    )

    latency_ms = int((time.monotonic() - start) * 1000)
    message = response.choices[0].message.content or ""
    usage = response.usage

    # 행운 아이템 파싱
    luck_item = _parse_luck_item(message)

    return LLMResult(
        content=message,
        luck_item=luck_item,
        prompt_tokens=usage.prompt_tokens if usage else 0,
        completion_tokens=usage.completion_tokens if usage else 0,
        total_tokens=usage.total_tokens if usage else 0,
        latency_ms=latency_ms,
        model_name=model,
    )


def _parse_luck_item(content: str) -> str:
    """
    LLM 응답 마지막 줄에서 "행운 아이템: XXX" 파싱.
    없으면 빈 문자열 반환.
    """
    for line in reversed(content.splitlines()):
        line = line.strip()
        if line.startswith("행운 아이템:"):
            return line.replace("행운 아이템:", "").strip()
    return ""
