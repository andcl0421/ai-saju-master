# 📂 05_ai_logic.md (Final)
## AI Fortune & Compatibility Logic Design

---

## 1. 개요 (Overview)
본 문서는 '만세력 AI 서비스'의 운세 생성 및 궁합 분석 로직을 정의한다.  
MVP 단계에서는 **Rule-based Score Engine + LLM Generation 구조**를 채택하여 정확도, 비용 효율성, 시스템 안정성을 확보한다.

AI는 모든 운세를 직접 생성하는 것이 아니라,  
**점수 계산 및 운세 상태 결정은 백엔드 로직에서 수행하고, LLM은 최종 해석 문장 생성 역할만 담당한다.**

---

## 2. AI 시스템 전체 구조 (AI Architecture)

### 2.1 오늘의 운세 생성 전체 흐름
```
User Request
    ↓
User Email → Profile 조회
    ↓
사주 간지 데이터 로드 (Year/Month/Day/Time Ganji)
    ↓
오늘 날짜 간지 계산
    ↓
Score Engine 실행
    ↓
운세 점수 생성
    ↓
Fortune Type 결정 (GOOD / NORMAL / BAD)
    ↓
fortune_phrases 템플릿 조회
    ↓
LLM Prompt 생성
    ↓
LLM 운세 문장 생성
    ↓
daily_fortunes DB 저장
    ↓
User Response
```

---

## 3. 운세 점수 생성 로직 (Score Engine)

### 3.1 점수 산출 공식
```
Final Score =
    Base Score (50)
  + Element Match Score (±20)
  + Today Relation Score (±25)
  + Random Variance (±5)
```

### 3.2 세부 운세 점수 산출 기준

| 운세 종류 | 핵심 오행 관계 | 가중치 기준 |
| :--- | :--- | :--- |
| **재물운** | 금(金), 토(土) | 일간(日干)과 재성(財星) 관계 |
| **연애운** | 화(火) | 관성(官星) 또는 합(合) 관계 |
| **건강운** | 수(水) | 오행 균형 및 충(冲) 여부 |
| **직장운** | 목(木) | 인성(印星), 비겁(比劫) 흐름 |

각 운세 점수는 개별 계산 후 평균 또는 가중 평균으로 `fortune_score` 산출.

---

## 4. 운세 상태 분류 (Fortune Type Classification)

| 점수 범위 | 운세 상태 |
|-----------|-----------|
| 80 ~ 100 | GOOD |
| 60 ~ 79 | NORMAL |
| 40 ~ 59 | BAD |
| 0 ~ 39 | VERY BAD |

운세 상태는 LLM 프롬프트 톤 조절 및 문장 템플릿 선택에 사용된다.

---

## 5. 궁합 분석 로직 (Compatibility Analysis)

### 5.1 궁합 분석 특징
- 실시간 분석 서비스
- 결과는 데이터베이스에 저장하지 않음 (Stateless)
- 요청 시마다 계산

### 5.2 궁합 분석 흐름
```
Profile A 조회
Profile B 조회
    ↓
일간(日干) 관계 분석
일지(日支) 합/충 분석
오행 분포 비교
    ↓
궁합 점수 계산
    ↓
LLM 궁합 해석 생성
    ↓
결과 반환
```

### 5.3 궁합 결과 구성
- 궁합 점수 (0 ~ 100)
- 관계 유형 (천생연분, 상호보완, 보통, 주의 필요)
- 궁합 해석
- 관계 조언

---

## 6. Fortune Phrase Template System

운세 문장 생성 비용을 줄이고 일관된 톤을 유지하기 위해  
`fortune_phrases` 테이블을 운세 문장 템플릿 저장소로 사용한다.

### 운세 생성 방식
```
운세 점수 계산
→ 운세 상태 결정
→ fortune_phrases 템플릿 조회
→ LLM이 템플릿 기반으로 문장 확장
→ 최종 운세 문장 생성
```

즉,
```
Rule Engine → 구조/점수 결정
LLM → 자연어 해석 생성
```

---

## 7. AI 로그 및 비용 관리 (Monitoring & Logging)

### 로그 저장 테이블
`fortune_logs`

### 저장 항목
| 컬럼 | 설명 |
|------|------|
| user_email | 사용자 식별 |
| profile_id | 사주 프로필 |
| prompt | LLM 프롬프트 |
| response | LLM 응답 |
| token_usage | 사용 토큰 |
| created_at | 생성 시간 |

### 목적
- LLM 비용 추적
- 프롬프트 개선
- 결과 품질 분석
- 오류 디버깅
- A/B 테스트

---

## 8. 향후 확장 계획 (Future RAG Structure)

서비스 고도화 단계에서 **Vector DB (ChromaDB)** 기반 RAG 구조를 도입한다.

### Vector DB 저장 데이터
- 명리학 고전 텍스트
- 일간 성격 해석
- 오행 특징 설명
- 간지 관계 해석
- 궁합 규칙
- 직업 운 해석
- 재물 운 해석
- 건강 운 해석
- 대운 / 세운 해석

### RAG 구조
```
사주 간지 데이터
    ↓
Vector DB 유사도 검색
    ↓
관련 명리학 규칙 Context 생성
    ↓
LLM 분석
    ↓
운세 / 궁합 / 직업 / 인생운 생성
```

---

## 9. 전체 AI 시스템 구조 요약

```
[User]
   ↓
[Profile DB]
   ↓
[Saju / Ganji Data]
   ↓
[Score Engine]
   ↓
[Fortune Type Decision]
   ↓
[Phrase Template]
   ↓
[LLM Generation]
   ↓
[Daily Fortune DB]
   ↓
[User Response]
```

궁합 분석 시스템:
```
Profile A
Profile B
   ↓
Compatibility Engine
   ↓
LLM Analysis
   ↓
Result Return
```

---