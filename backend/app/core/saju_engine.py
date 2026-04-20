from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import date

CHEONGAN: list[str] = ["갑", "을", "병", "정", "무", "기", "경", "신", "임", "계"]
JIJI: list[str] = ["자", "축", "인", "묘", "진", "사", "오", "미", "신", "유", "술", "해"]

CHEONGAN_ELEMENT: list[str] = [
    "목",
    "목",
    "화",
    "화",
    "토",
    "토",
    "금",
    "금",
    "수",
    "수",
]
JIJI_ELEMENT: list[str] = [
    "수",
    "토",
    "목",
    "목",
    "토",
    "화",
    "화",
    "토",
    "금",
    "금",
    "토",
    "수",
]

_DAY_GANJI_BASE_DATE = date(1900, 1, 1)
_DAY_GANJI_BASE_INDEX = 10
_YEAR_STEM_TO_MONTH_STEM_BASE: dict[int, int] = {
    0: 2,
    5: 2,
    1: 4,
    6: 4,
    2: 6,
    7: 6,
    3: 8,
    8: 8,
    4: 0,
    9: 0,
}
_DAY_STEM_TO_HOUR_STEM_BASE: dict[int, int] = {
    0: 0,
    5: 0,
    1: 2,
    6: 2,
    2: 4,
    7: 4,
    3: 6,
    8: 6,
    4: 8,
    9: 8,
}
_GENERATING: dict[str, str] = {"목": "화", "화": "토", "토": "금", "금": "수", "수": "목"}
_CONTROLLING: dict[str, str] = {"목": "토", "토": "수", "수": "화", "화": "금", "금": "목"}


@dataclass
class GanjiResult:
    year_ganji: str
    month_ganji: str
    day_ganji: str
    time_ganji: str
    five_elements: dict[str, int]
    calculated_birth_time: str
    is_time_unknown: bool


def _index_to_ganji(index: int) -> str:
    return CHEONGAN[index % 10] + JIJI[index % 12]


def _ganji_cheongan_index(ganji: str) -> int:
    return CHEONGAN.index(ganji[0])


def _ganji_jiji_index(ganji: str) -> int:
    return JIJI.index(ganji[1])


def calculate_year_ganji(year: int) -> str:
    return _index_to_ganji((year - 4) % 60)


def calculate_day_ganji(target: date) -> str:
    delta = (target - _DAY_GANJI_BASE_DATE).days
    return _index_to_ganji((_DAY_GANJI_BASE_INDEX + delta) % 60)


def calculate_month_ganji(year: int, month: int) -> str:
    year_stem_idx = _ganji_cheongan_index(calculate_year_ganji(year))
    stem_idx = (_YEAR_STEM_TO_MONTH_STEM_BASE[year_stem_idx] + month - 1) % 10
    branch_idx = (month + 1) % 12
    return CHEONGAN[stem_idx] + JIJI[branch_idx]


def calculate_time_ganji(day_ganji: str, hour: int) -> str:
    branch_idx = 0 if hour >= 23 else (hour + 1) // 2
    day_stem_idx = _ganji_cheongan_index(day_ganji)
    stem_idx = (_DAY_STEM_TO_HOUR_STEM_BASE[day_stem_idx] + branch_idx) % 10
    return CHEONGAN[stem_idx] + JIJI[branch_idx]


def calculate_five_elements(*ganji_list: str) -> dict[str, int]:
    counts: dict[str, int] = {"목": 0, "화": 0, "토": 0, "금": 0, "수": 0}
    for ganji in ganji_list:
        if len(ganji) != 2:
            continue
        counts[CHEONGAN_ELEMENT[CHEONGAN.index(ganji[0])]] += 1
        counts[JIJI_ELEMENT[JIJI.index(ganji[1])]] += 1
    return counts


def calculate_ganji(birth_date: date, birth_time: str) -> GanjiResult:
    is_time_unknown = birth_time == "UNKNOWN" or not birth_time
    calculated_birth_time = "12:00" if is_time_unknown else birth_time
    hour = int(calculated_birth_time.split(":")[0])

    year_ganji = calculate_year_ganji(birth_date.year)
    month_ganji = calculate_month_ganji(birth_date.year, birth_date.month)
    day_ganji = calculate_day_ganji(birth_date)
    time_ganji = calculate_time_ganji(day_ganji, hour)

    return GanjiResult(
        year_ganji=year_ganji,
        month_ganji=month_ganji,
        day_ganji=day_ganji,
        time_ganji=time_ganji,
        five_elements=calculate_five_elements(year_ganji, month_ganji, day_ganji, time_ganji),
        calculated_birth_time=calculated_birth_time,
        is_time_unknown=is_time_unknown,
    )


def _element_relation_score(birth_element: str, today_element: str) -> int:
    if birth_element == today_element:
        return 20
    if _GENERATING.get(today_element) == birth_element:
        return 15
    if _GENERATING.get(birth_element) == today_element:
        return 10
    if _CONTROLLING.get(today_element) == birth_element:
        return -15
    if _CONTROLLING.get(birth_element) == today_element:
        return -10
    return 0


def _today_relation_score(birth_day_ganji: str, today_ganji: str) -> int:
    birth_branch = _ganji_jiji_index(birth_day_ganji)
    today_branch = _ganji_jiji_index(today_ganji)
    diff = abs(birth_branch - today_branch)

    if diff == 6:
        return -25

    liu_he = [{0, 1}, {2, 11}, {3, 10}, {4, 9}, {5, 8}, {6, 7}]
    if {birth_branch, today_branch} in liu_he:
        return 25

    san_he = [{8, 0, 4}, {11, 3, 7}, {2, 6, 10}, {5, 9, 1}]
    for group in san_he:
        if birth_branch in group and today_branch in group:
            return 20

    xing = [{0, 3}, {2, 5}, {1, 10}]
    self_xing = {4, 6, 9, 11}
    if {birth_branch, today_branch} in xing:
        return -15
    if birth_branch in self_xing and birth_branch == today_branch:
        return -15

    return 0


def calculate_scores(
    profile_day_ganji: str,
    today_ganji: str,
    *,
    seed: int | None = None,
) -> dict[str, int]:
    rng = random.Random(seed)

    birth_element = CHEONGAN_ELEMENT[_ganji_cheongan_index(profile_day_ganji)]
    today_element = CHEONGAN_ELEMENT[_ganji_cheongan_index(today_ganji)]
    base = 50 + _element_relation_score(birth_element, today_element)
    base += _today_relation_score(profile_day_ganji, today_ganji)
    base += rng.randint(-5, 5)
    fortune_score = max(0, min(100, base))

    def _sub_score() -> int:
        return max(0, min(100, base + rng.randint(-12, 12)))

    return {
        "fortune_score": fortune_score,
        "money_score": _sub_score(),
        "love_score": _sub_score(),
        "health_score": _sub_score(),
        "work_score": _sub_score(),
    }


def get_fortune_type(fortune_score: int) -> str:
    if fortune_score >= 80:
        return "GOOD"
    if fortune_score >= 60:
        return "NORMAL"
    if fortune_score >= 40:
        return "BAD"
    return "VERY_BAD"
