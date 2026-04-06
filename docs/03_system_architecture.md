# 📂 03_system_architecture.md
## System Architecture & Data Flow (v1.2 Final)

---

## 1. 개요 (Overview)
본 문서는 '만세력 AI 서비스'의 전체 시스템 구성과 데이터 흐름을 정의한다. 
사용자 식별은 **이메일(Email)**을 유일한 식별자로 사용하며, 별도의 프레임워크(LangChain 등) 없이 **OpenAI 네이티브 Function Calling**을 통해 사주 계산 및 분석 도구를 직접 제어한다.

---

## 2. 시스템 구성도 (System Diagram)
```
[ Client Layer ]
    React (SPA)
          ↓ ↑ (REST API / JSON)

[ Application Layer ]
    FastAPI (Back-end Server)
          ↓

 ┌──────────────────────────────────────┐
 │           AI & Data Layer            │
 │                                      │
 │  - PostgreSQL (User / Profiles / Logs)│
 │  - ChromaDB (RAG Knowledge)          │
 │                                      │
 │  - OpenAI API (LLM + Function Calling)│
 │  - Tool Layer (Ganji / External Data)│
 └──────────────────────────────────────┘
```

---

## 3. 핵심 구성 요소 (Components)

| 구성요소 | 역할 | 기술 스택 |
| :--- | :--- | :--- |
| **프론트엔드** | 사용자 입력 및 결과 시각화 | React |
| **백엔드** | **Function Calling 직접 제어** 및 API 서빙 | FastAPI |
| **메인 DB** | **이메일 기반 계정**, 프로필 및 운세 저장 | PostgreSQL |
| **벡터 DB** | 명리 해석 규칙 및 지식 데이터 저장/검색 | ChromaDB (RAG) |
| **LLM API** | **만세력 계산기 및 외부 도구 호출 판단** | OpenAI (GPT-4o) |

---

## 4. 데이터 흐름 (Data Flow)

### 4.1 오늘의 운세 생성 (Direct Tool Flow)
1. **사용자 확인:** 입력된 **이메일**로 `users` 테이블 조회 및 연결된 프로필 로드.
2. **캐시 확인:** `daily_fortunes`에 오늘 날짜 데이터가 있는지 확인 (있으면 즉시 반환).
3. **도구 판단 (Function Calling):** LLM이 분석에 필요한 만세력 도구(`get_ganji`) 등을 호출하도록 백엔드가 직접 제어.
4. **지식 보강 (RAG):** 도구 결과값을 키워드로 벡터 DB에서 관련 명리 해석문 검색.
5. **저장 및 반환:** 최종 생성된 운세를 PostgreSQL에 저장 후 클라이언트에 응답.

### 4.2 궁합 분석 흐름 (Compatibility Flow)
- **특징**: Stateless(무상태) 처리, 실시간 분석.
- **흐름**: 프로필 A/B 조회 → LLM 분석(Function Calling) → 결과 즉시 반환 (**DB 저장 안 함**).

---

## 5. 인프라 및 운영 설계 (Infrastructure)
- **Container**: Docker / Docker Compose (로컬 및 운영 환경 통일)
- **Cloud**: AWS EC2 (Server), AWS RDS (PostgreSQL)
- **CI/CD**: GitHub Actions (자동 배포)
- **Monitoring**: AI API 사용량(Token) 추적 및 에러 로그 트래킹

---

## 6. 아키텍처 핵심 특징 (Key Characteristics)
1. **No Framework**: 랭체인/랭그래프를 사용하지 않아 오버헤드가 없고 디버깅이 직관적임.
2. **Email Identity**: UUID 대신 이메일을 유니크 키로 사용하여 사용자 관리 단순화.
3. **Hybrid AI 구조**: RAG와 LLM의 결합으로 답변 신뢰도 향상 및 비용 절감.
4. **캐싱 전략**: 동일 일자 운세 재사용을 통한 API 호출 최소화.

---

## 7. 현재 상태 및 요약
- **Summary**: `이메일 입력 → 프로필 조회 → 도구 호출(AI) → 결과 저장 → 응답`
- **Status**: **설계 완료 (이메일 식별 및 네이티브 Function Calling 구조 확정)**