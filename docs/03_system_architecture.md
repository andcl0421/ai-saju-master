# 📂 03_system_architecture.md
## System Architecture & Data Flow (v1.1 Final)

---

## 1. 개요 (Overview)
본 문서는 '만세력 AI 서비스'의 전체 시스템 구성과 구성 요소 간의 상호작용, 그리고 데이터 흐름(Data Flow)을 정의한다. 본 시스템은 **3-Tier Architecture + AI Layer (RAG + LLM)** 구조를 기반으로 설계된다.

---

## 2. 시스템 구성도 (System Diagram)
```
[ Client Layer ]
    React / Web / App
          ↓ ↑
[ Application Layer ]
    FastAPI (REST API Server)
          ↓
 ┌───────────────────────────────┐
 │        Data Layer             │
 │   PostgreSQL (Main DB)        │
 └───────────────┬───────────────┘
                 ↓
        [ AI Intelligence Layer ]
      LLM (OpenAI / Claude API)
                 ↓
        [ Vector Database ]
      ChromaDB / Pinecone
```

---

## 3. 핵심 구성 요소 (Components)
| 구성 요소 | 역할 | 비고 |
|:---|:---|:---|
| **Frontend** | 사용자 입력 및 결과 UI | React / SPA |
| **Backend** | 요청 처리, 비즈니스 로직 | FastAPI |
| **Main DB** | 사용자, 프로필, 운세 저장 | PostgreSQL |
| **Vector DB** | 사주 해석 규칙 저장 | ChromaDB / RAG |
| **LLM API** | 운세 및 궁합 문장 생성 | OpenAI / Claude |
| **Scheduler** | 매일 아침 운세 생성 트리거 | APScheduler |
| **Push Server** | 푸시 알림 전송 | Firebase FCM |

---

## 4. 데이터 흐름 (Data Flow)

### 4.1 오늘의 운세 생성 흐름 (Daily Fortune Flow)
`[Client]` → `[API Server]` → `[PostgreSQL (간지 조회)]` → `[Vector DB (RAG 검색)]` → `[LLM API (생성)]` → `[PostgreSQL (저장)]` → `[Client (반환)]`

### 4.2 궁합 분석 흐름 (Compatibility Flow)
- **특징**: Stateless 처리, 비용 최적화, 빠른 응답.
- **흐름**: 프로필 A/B 조회 후 LLM 분석 결과 즉시 반환 (**DB 저장 없음**).

### 4.3 푸시 알림 및 스케줄러 흐름 (Push Flow)
- **특징**: 자동 운세 생성, 캐싱 활용 (중복 생성 방지).
- **흐름**: 스케줄러 트리거 → 대표 프로필 조회 → 운세 생성/조회 → FCM 전송.

---

## 5. 인프라 및 운영 설계 (Infrastructure)
- **Container**: Docker / Docker Compose
- **Cloud**: AWS EC2 (Server), AWS RDS (PostgreSQL)
- **CI/CD**: GitHub Actions
- **Monitoring**: AI API 사용량 추적 및 에러 로그 트래킹

---

## 6. 아키텍처 핵심 특징 (Key Characteristics)
1. **Hybrid AI 구조**: RAG와 LLM의 결합으로 비용 절감 및 해석 품질 향상.
2. **캐싱 전략**: `(profile_id, target_date)` 기반으로 동일 일자 운세 재사용.
3. **Stateless API**: 궁합 분석 등 일회성 데이터는 저장하지 않아 서버 부하 최소화.
4. **확장성**: 모듈화된 설계를 통해 AI 모델 및 DB의 유연한 교체 가능.

---

## 7. 현재 상태 및 요약
- **Summary**: `User → API → DB → RAG → LLM → DB 저장 → 응답`
- **Status**: **설계 완료 (구현 대기 상태)**