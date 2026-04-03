# 📂 05_ai_logic.md
## AI Fortune & Compatibility Logic Design

---

## 1. 개요 (Overview)
본 문서는 만세력 AI 서비스의 운세 생성, 궁합 분석, 점수 산출 등 AI 로직의 전체 구조와 데이터 흐름을 정의한다. AI 시스템은 **Hybrid 구조 (RAG + LLM)** 방식으로 동작한다.

**구성 요소:**
- 사주 간지 데이터
- 운세 규칙 데이터 (Vector DB)
- LLM (운세 문장 생성)
- 점수 생성 로직
- 캐싱 DB

---

## 2. AI 시스템 전체 구조 (AI Architecture)

**전체 운세 생성 흐름:**
```
사용자 프로필 조회
→ 사주 간지 데이터 로드
→ Vector DB에서 운세 규칙 검색 (RAG)
→ LLM 프롬프트 생성
→ 운세 문장 생성
→ 점수 계산
→ DB 저장
→ 사용자 반환
```

**구성 시스템:**
- Backend Server / LLM API
- Vector Database / Fortune Database
- Scheduler / Push Server

---

## 3. 오늘의 운세 생성 로직 (Daily Fortune Logic)

### 3.1 운세 생성 흐름
1. `profile_id` 입력 → `saju_profiles` 테이블 조회
2. 간지 데이터 추출 및 오늘 날짜 기준 운세 규칙 검색
3. Vector DB 유사도 검색 및 Context 생성
4. LLM Prompt 생성 및 운세 문장 생성
5. 점수 생성 → `daily_fortunes` 테이블 저장 → 결과 반환

### 3.2 운세 생성 구조 (Hybrid 방식)
운세는 아래 방식으로 생성된다.
- **규칙 기반 (RAG 검색)**: 60%
- **LLM 문장 생성**: 40%
- **결과**: 최종 운세 도출

---

## 4. 운세 점수 생성 로직 (Score System)

| 항목 | 설명 | 점수 범위 |
|------|------|------|
| fortune_score | 전체 운세 | 0 ~ 100 |
| money_score | 재물운 | 0 ~ 100 |
| love_score | 연애운 | 0 ~ 100 |
| health_score | 건강운 | 0 ~ 100 |
| work_score | 직업/학업운 | 0 ~ 100 |

**점수 생성 방식:**
`기본 점수 + 간지 상생/상극 가중치 + 오늘 일진 영향 + 랜덤 편차 (±5) = 최종 점수`

---

## 5. 궁합 분석 로직 (Compatibility Logic)

**궁합 분석 흐름:**
1. 프로필 A/B 간지 조회 → 오행 상생/상극 계산
2. 궁합 규칙 검색 (Vector DB) → LLM 분석 프롬프트 생성
3. 결과 생성 (점수, 요약, 관계 유형, 조언) → **결과 즉시 반환 (DB 미저장)**

---

## 6. Vector DB 및 캐싱 전략

### 6.1 Vector DB 데이터 종류
- 일간 성격, 오행 특징, 간지 관계, 오늘 일진 해석, 운세 문장 템플릿, 궁합/직업/재물/건강 운 해석 등.

### 6.2 캐싱 및 스케줄러
- **캐싱 키**: `(profile_id, target_date)`
- **스케줄러**: 매일 오전 7시 실행 (대표 프로필 조회 → 운세 생성 → 저장 → 푸시 발송)

---

## 7. AI 로그 저장 (AI Generation Logs)
- **테이블**: `ai_generation_logs`
- **저장 데이터**: `profile_id`, `prompt`, `response`, `token_usage`, `created_at`
- **목적**: 비용 추적, 품질 개선, 오류 분석, 프롬프트 개선

---

## 8. Fortune Generation Pipeline

오늘의 운세 생성 시 LLM(Large Language Model)에 입력되는 데이터 구조와 처리 단계는 다음과 같다.

### 8.1 LLM 입력 데이터 구성 (Input Data)
AI가 정확한 해석을 내릴 수 있도록 다음의 데이터를 컨텍스트(Context)로 제공한다.
- **사용자 사주 간지**: 년(年), 월(月), 일(日), 시(時)의 8글자 정보
- **오행 분포**: 목(木), 화(火), 토(土), 금(金), 수(水)의 비율 분석 데이터
- **오늘 날짜 및 일진**: 운세를 산출할 당일의 간지 정보
- **운세 규칙 (RAG)**: Vector DB에서 검색된 해당 사주 조합에 대한 고전 명리학 규칙
- **운세 문장 템플릿**: 서비스 고유의 톤앤매너를 유지하기 위한 문장 가이드

### 8.2 LLM 입력 구조 (Prompt Structure)
효율적인 추론을 위해 아래와 같은 순서로 프롬프트를 구성한다.
1. **사용자 사주 정보**: 대상의 타고난 기운 정의
2. **오늘 일진 정보**: 현재 흐르는 운의 흐름 제시
3. **관련 운세 규칙 Context**: 명리학적 근거 데이터 삽입
4. **운세 생성 요청 Prompt**: 페르소나(명리학자) 부여 및 생성 지침
5. **JSON 형식 결과 생성**: 시스템 연동을 위한 규격화된 출력 요구 (점수 및 본문)

---