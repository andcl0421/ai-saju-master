# 📂 07_prompt_design.md
## LLM Prompt Design Specification (v1.2)

---

## 1. 개요 (Overview)
본 문서는 만세력 AI 서비스에서 사용하는 LLM 프롬프트 구조, 출력 형식, 모델 설정 및 프롬프트 버전 관리 전략을 정의한다. 모든 AI 응답은 시스템 연동의 안정성을 위해 **JSON 형식**으로 반환하도록 설계한다.

---

## 2. System Prompt (시스템 프롬프트)
```text
You are a professional Saju (Korean astrology) analyst.
You analyze fortune based on Four Pillars of Destiny.
Always respond in Korean.
Always return the result in JSON format.
Do not include any text outside JSON.
Your analysis should be realistic, balanced, and not overly deterministic.
```

---

## 3. 오늘의 운세 Prompt (Daily Fortune)
**[Input 데이터]**
- 사용자 사주 간지(년/월/일/시), 오행 분포, 오늘 일진, RAG 규칙 Context

**[Prompt Template]**
```text
사용자의 사주 정보와 오늘의 일진을 기반으로 오늘의 운세를 분석하라.

[사주 정보]
- 년주: {year_ganji} / 월주: {month_ganji} / 일주: {day_ganji} / 시주: {time_ganji}

[오행 분포]
{five_elements}

[오늘 일진]
{today_ganji}

[운세 규칙]
{rag_context}

다음 JSON 형식으로 오늘의 운세를 생성하라.
```

---

## 4. 궁합 분석 Prompt (Compatibility)
```text
두 사람의 사주를 비교하여 궁합을 분석하라.

[사람 A 사주]: {ganji_a}
[사람 B 사주]: {ganji_b}

오행 상생과 상극 관계를 기반으로 관계 궁합을 분석하라.
결과는 다음 JSON 형식으로 생성하라. (결과는 실시간 반환용이며 DB에 저장되지 않음)
```

---

## 5. AI Output JSON Format
**[오늘의 운세 Output]**
```json
{
  "fortune_score": 0,
  "money_score": 0,
  "love_score": 0,
  "health_score": 0,
  "work_score": 0,
  "summary": "",
  "advice": "",
  "luck_item": ""
}
```

---

## 6. Model Parameters & Optimization
- **Model**: GPT / Claude (Temperature: 0.7, Max Tokens: 800)
- **전략**: Few-shot 예시를 통해 JSON 출력 안정화 및 점수-문장 간의 일관성 유지.
- **버전 관리**: v1(기본) -> v5(점수 로직 개선)까지 단계별 업데이트 기록.

---

## 7. Prompt Flow (AI 호출 흐름)

AI 서비스가 호출되어 결과가 반환되기까지의 전체 기술적 흐름은 다음과 같다.

1. **사용자 요청**: 클라이언트로부터 오늘 운세 또는 궁합 분석 요청 수신.
2. **프로필 간지 데이터 조회**: `saju_profiles` 테이블에서 대상자의 4주 8자 데이터 로드.
3. **Vector DB 검색 (RAG)**: 해당 사주와 오늘 일진에 적합한 명리학 규칙 및 해석 컨텍스트 검색.
4. **Prompt Template 생성**: 동적 데이터(간지, RAG 결과 등)를 템플릿 변수에 매핑.
5. **Prompt 결합**: 미리 정의된 `System Prompt`와 생성된 `User Prompt`를 하나로 결합.
6. **LLM API 호출**: 설정된 모델 파라미터(Temperature 0.7 등)와 함께 LLM에 요청 전달.
7. **JSON 결과 반환**: LLM으로부터 구조화된 JSON 데이터 수신.
8. **JSON Validation**: 수신된 데이터가 정의된 규격(Schema)에 맞는지 검증 및 예외 처리.
9. **DB 저장 (운세 한정)**: 검증된 결과를 `daily_fortunes`에 저장 (궁합은 저장 없이 통과).
10. **API 응답 반환**: 최종 데이터를 JSON 형태로 클라이언트에 전송.

---