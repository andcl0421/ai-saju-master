"""
core/saju_engine.py
순수 계산 로직만 포함합니다. DB·네트워크·비즈니스 로직 없음.

60갑자 계산 공식
  - 연간지: (year - 4) % 60
  - 일간지: 기준일(1900-01-01 = 甲戌, index=10) 기준 오프셋
  - 월간지: 연간지 천간에서 파생
  - 시간지: 일간지 천간에서 파생
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import date, datetime

# ─────────────────────────────────────────────
# 상수
# ─────────────────────────────────────────────
CHEONGAN: list[str] = ["갑", "을", "병", "정", "무", "기", "경", "신", "임", "계"]
JIJI: list[str] = ["자", "축", "인", "묘", "진", "사", "오", "미", "신", "유", "술", "해"]

# 천간 → 오행 (index 기준)
CHEONGAN_ELEMENT: list[str] = [
    "목", "목",   # 갑, 을
    "화", "화",   # 병, 정
    "토", "토",   # 무, 기
    "금", "금",   # 경, 신
    "수", "수",   # 임, 계
]

# 지지 → 오행 (index 기준)
JIJI_ELEMENT: list[str] = [
    "수", "토", "목", "목",   # 자, 축, 인, 묘
    "토", "화", "화", "토",   # 진, 사, 오, 미
    "금", "금", "토", "수",   # 신, 유, 술, 해
]

# 1900-01-01 기준 일간지 index (甲戌 = 10)
_DAY_GANJI_BASE_DATE = date(1900, 1, 1)
_DAY_GANJI_BASE_INDEX = 10

# 연간지 천간 → 월 천간 시작점
# 갑·기년=병(2), 을·경년=무(4), 병·신년=경(6), 정·임년=임(8), 무·계년=갑(0)
_YEAR_STEM_TO_MONTH_STEM_BASE: dict[int, int] = {
    0: 2, 5: 2,   # 갑, 기
    1: 4, 6: 4,   # 을, 경
    2: 6, 7: 6,   # 병, 신
    3: 8, 8: 8,   # 정, 임
    4: 0, 9: 0,   # 무, 계
}

# 일간지 천간 → 시 천간 시작점
_DAY_STEM_TO_HOUR_STEM_BASE: dict[int, int] = {
    0: 0, 5: 0,   # 갑, 기
    1: 2, 6: 2,   # 을, 경
    2: 4, 7: 4,   # 병, 신
    3: 6, 8: 6,   # 정, 임
    4: 8, 9: 8,   # 무, 계
}

# 오행 상생·상극 관계 (score 계산에 사용)
_GENERATING: dict[str, str] = {
    "목": "화", "화": "토", "토": "금", "금": "수", "수": "목"
}
_CONTROLLING: dict[str, str] = {
    "목": "토", "화": "금", "토": "수", "금": "목", "수": "화"
}


# ─────────────────────────────────────────────
# 결과 데이터클래스
# ─────────────────────────────────────────────
@dataclass
class GanjiResult:
    year_ganji: str
    month_ganji: str
    day_ganji: str
    time_ganji: str
    five_elements: dict[str, int]   # {"목": 2, "화": 1, ...}
    calculated_birth_time: str      # 실제 계산에 사용된 시간 (UNKNOWN → "12:00")
    is_time_unknown: bool


# ─────────────────────────────────────────────
# 내부 헬퍼
# ─────────────────────────────────────────────
def _index_to_ganji(index: int) -> str:
    """0~59 index → 갑자 형식 문자열"""
    return CHEONGAN[index % 10] + JIJI[index % 12]


def _ganji_cheongan_index(ganji: str) -> int:
    """간지 문자열의 천간 index 반환"""
    return CHEONGAN.index(ganji[0])


def _ganji_jiji_index(ganji: str) -> int:
    """간지 문자열의 지지 index 반환"""
    return JIJI.index(ganji[1])


# ─────────────────────────────────────────────
# 공개 계산 함수
# ─────────────────────────────────────────────
def calculate_year_ganji(year: int) -> str:
    """연 간지 계산. 예) 2024 → '갑진'"""
    index = (year - 4) % 60
    return _index_to_ganji(index)


def calculate_day_ganji(target: date) -> str:
    """일 간지 계산. 기준: 1900-01-01 = 甲戌(index 10)"""
    delta = (target - _DAY_GANJI_BASE_DATE).days
    index = (_DAY_GANJI_BASE_INDEX + delta) % 60
    return _index_to_ganji(index)


def calculate_month_ganji(year: int, month: int) -> str:
    """
    월 간지 계산.
    지지: 1월=인(2), 2월=묘(3), ..., 12월=축(1)
    천간: 연간지 천간에 따른 시작점 + (month - 1)
    """
    year_ganji = calculate_year_ganji(year)
    year_stem_idx = _ganji_cheongan_index(year_ganji)
    stem_base = _YEAR_STEM_TO_MONTH_STEM_BASE[year_stem_idx]

    stem_idx = (stem_base + month - 1) % 10
    branch_idx = (month + 1) % 12   # 1월=인(2), 2월=묘(3), ..., 12월=축(1)
    return CHEONGAN[stem_idx] + JIJI[branch_idx]


def calculate_time_ganji(day_ganji: str, hour: int) -> str:
    """
    시 간지 계산.
    지지: 자시(23-1시)=0, 축시(1-3시)=1, ..., 해시(21-23시)=11
    천간: 일간지 천간에 따른 시작점 + 시지 index
    """
    # 자시(子時) 분기: 23:00 이상이면 다음 날 자시
    if hour >= 23:
        branch_idx = 0
    else:
        branch_idx = (hour + 1) // 2

    day_stem_idx = _ganji_cheongan_index(day_ganji)
    stem_base = _DAY_STEM_TO_HOUR_STEM_BASE[day_stem_idx]
    stem_idx = (stem_base + branch_idx) % 10
    return CHEONGAN[stem_idx] + JIJI[branch_idx]


def calculate_five_elements(*ganji_list: str) -> dict[str, int]:
    """
    주어진 간지 목록의 오행 분포 집계.
    천간 + 지지 각각 1개씩 카운트.
    """
    counts: dict[str, int] = {"목": 0, "화": 0, "토": 0, "금": 0, "수": 0}
    for ganji in ganji_list:
        if len(ganji) != 2:
            continue
        stem_idx = CHEONGAN.index(ganji[0])
        branch_idx = JIJI.index(ganji[1])
        counts[CHEONGAN_ELEMENT[stem_idx]] += 1
        counts[JIJI_ELEMENT[branch_idx]] += 1
    return counts


def calculate_ganji(birth_date: date, birth_time: str) -> GanjiResult:
    """
    사주 사주(연·월·일·시) 간지 계산 진입점.

    Parameters
    ----------
    birth_date  : 생년월일
    birth_time  : "HH:MM" 또는 "UNKNOWN"
                  UNKNOWN 이면 12:00(정오)로 보정
    """
    is_time_unknown = (birth_time == "UNKNOWN" or not birth_time)
    calc_time = "12:00" if is_time_unknown else birth_time

    hour = int(calc_time.split(":")[0])

    year_ganji = calculate_year_ganji(birth_date.year)
    month_ganji = calculate_month_ganji(birth_date.year, birth_date.month)
    day_ganji = calculate_day_ganji(birth_date)
    time_ganji = calculate_time_ganji(day_ganji, hour)

    five_elements = calculate_five_elements(
        year_ganji, month_ganji, day_ganji, time_ganji
    )

    return GanjiResult(
        year_ganji=year_ganji,
        month_ganji=month_ganji,
        day_ganji=day_ganji,
        time_ganji=time_ganji,
        five_elements=five_elements,
        calculated_birth_time=calc_time,
        is_time_unknown=is_time_unknown,
    )


# ─────────────────────────────────────────────
# Score Engine (운세 점수 산출)
# ─────────────────────────────────────────────
def _element_relation_score(birth_element: str, today_element: str) -> int:
    """
    오행 관계에 따른 Element Match Score.
      같은 오행        : +20
      상생(나를 생함)  : +15
      상생(내가 생함)  : +10
      상극(나를 극함)  : -15
      상극(내가 극함)  : -10
    """
    if birth_element == today_element:
        return 20
    if _GENERATING.get(today_element) == birth_element:   # today가 birth를 생
        return 15
    if _GENERATING.get(birth_element) == today_element:   # birth가 today를 생
        return 10
    if _CONTROLLING.get(today_element) == birth_element:  # today가 birth를 극
        return -15
    if _CONTROLLING.get(birth_element) == today_element:  # birth가 today를 극
        return -10
    return 0


def _today_relation_score(birth_day_ganji: str, today_ganji: str) -> int:
    """
    일지(日支) 충(冲) / 합(合) 관계에 따른 Today Relation Score.
      육합(六合)  : +25
      삼합(三合)  : +20
      충(冲, 6칸) : -25
      형(刑)      : -15
    """
    birth_branch = _ganji_jiji_index(birth_day_ganji)
    today_branch = _ganji_jiji_index(today_ganji)
    diff = abs(birth_branch - today_branch)

    # 충: 지지 index 차이 6
    if diff == 6:
        return -25

    # 육합 쌍: (자-축), (인-해), (묘-술), (진-유), (사-신), (오-미)
    LIU_HE = [{0, 1}, {2, 11}, {3, 10}, {4, 9}, {5, 8}, {6, 7}]
    if {birth_branch, today_branch} in LIU_HE:
        return 25

    # 삼합: (신-자-진), (해-묘-미), (인-오-술), (사-유-축)
    SAN_HE = [{8, 0, 4}, {11, 3, 7}, {2, 6, 10}, {5, 9, 1}]
    for group in SAN_HE:
        if birth_branch in group and today_branch in group:
            return 20

    # 형(자-묘, 인-사, 축-술, 진-진, 오-오, 유-유, 해-해)
    XING = [{0, 3}, {2, 5}, {1, 10}]
    SELF_XING = {4, 6, 9, 11}
    if {birth_branch, today_branch} in XING:
        return -15
    if birth_branch in SELF_XING and birth_branch == today_branch:
        return -15

    return 0


def calculate_scores(
    profile_day_ganji: str,
    today_ganji: str,
    *,
    seed: int | None = None,
) -> dict[str, int]:
    """
    운세 점수 산출.

    Returns
    -------
    {
        "fortune_score": 0~100,
        "money_score":   0~100,
        "love_score":    0~100,
        "health_score":  0~100,
        "work_score":    0~100,
    }
    """
    rng = random.Random(seed)

    # 일간지 오행
    birth_stem_idx = _ganji_cheongan_index(profile_day_ganji)
    today_stem_idx = _ganji_cheongan_index(today_ganji)
    birth_element = CHEONGAN_ELEMENT[birth_stem_idx]
    today_element = CHEONGAN_ELEMENT[today_stem_idx]

    element_score = _element_relation_score(birth_element, today_element)
    relation_score = _today_relation_score(profile_day_ganji, today_ganji)
    variance = rng.randint(-5, 5)

    base = 50 + element_score + relation_score + variance
    fortune_score = max(0, min(100, base))

    def _sub_score(extra_variance: int) -> int:
        v = rng.randint(-8, 8)
        return max(0, min(100, base + extra_variance + v))

    return {
        "fortune_score": fortune_score,
        "money_score": _sub_score(rng.randint(-10, 10)),
        "love_score": _sub_score(rng.randint(-10, 10)),
        "health_score": _sub_score(rng.randint(-10, 10)),
        "work_score": _sub_score(rng.randint(-10, 10)),
    }


def get_fortune_type(fortune_score: int) -> str:
    """점수 → 운세 유형 (GOOD / NORMAL / BAD / VERY_BAD)"""
    if fortune_score >= 80:
        return "GOOD"
    if fortune_score >= 60:
        return "NORMAL"
    if fortune_score >= 40:
        return "BAD"
    return "VERY_BAD"
