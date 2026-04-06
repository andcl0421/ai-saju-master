# 📂 07_prompt_design.md (v1.3 Final)
## LLM 프롬프트 설계서 (Prompt Specification)

---

## 1. 개요 (Overview)
본 문서는 '만세력 AI 서비스'의 프롬프트 구조, 출력 형식, 모델 설정 및 안정성 전략을 정의한다.

---

## 2. System Prompt (시스템 프롬프트)
```text
You are a professional Saju (Korean astrology) analyst.

Rules:
- Always respond in Korean.
- Always return a valid JSON object.
- Do NOT include any text outside JSON.
- Ensure all fields are present (null is forbidden).
- Keep interpretations realistic and balanced.
```

---

## 3. 기능별 프롬프트 템플릿

### 3.1 오늘의 운세 (Daily Fortune)
```text
[사주 정보]
- 년주: {year_ganji} / 월주: {month_ganji} / 일주: {day_ganji} / 시주: {time_ganji}
[오행 분포]: {five_elements}
[오늘 일진]: {today_ganji}
[참고 문장]: {fortune_phrases}

위 정보를 기반으로 0~100 사이의 점수와 상세 운세를 JSON 형식으로 생성하라.
```

---

## 4. Output JSON Schema (출력 규격)
```json
{
  "fortune_score": 0,
  "money_score": 0,
  "love_score": 0,
  "health_score": 0,
  "work_score": 0,
  "summary": "string",
  "advice": "string",
  "luck_item": "string"
}
```

---

## 5. 모델 설정 (Model Configuration)
- **Model**: gpt-4o
- **Temperature**: 0.7 (적절한 창의성)
- **Response Format**: `json_object` 강제

---

## 6. 안정성 및 캐싱 전략
- **캐싱**: `daily_fortunes` 테이블을 활용하여 하루 1회 초과 호출 방지 (비용 절감)
- **검증**: JSON 파싱 실패 시 최대 2회 재시도 (Retry) 로직 적용