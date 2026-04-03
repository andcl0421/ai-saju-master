# 🔮 AI 사주 Master: 만세력 기반 하이브리드 AI 운세 서비스
> **"정확한 만세력 데이터와 AI의 감성적인 해석의 만남"** > 회원가입 없이 사주를 저장하고, AI가 생성한 오늘의 운세를 제공하는 개인화 콘텐츠 시스템 프로젝트입니다.

---

# 🌟 Introduction
기존 사주 서비스들은 AI에게 모든 계산을 맡겨 답변이 부정확하거나, 매번 텍스트를 생성하기 때문에 비용이 계속 발생하는 문제가 있습니다.

**AI 사주 Master**는  
만세력 계산은 Python 라이브러리로 정확하게 처리하고,  
AI는 해석만 담당하도록 하는 **Hybrid 구조**를 설계하여 아래 4가지를 동시에 달성했습니다.

- **정확도 향상**: 전통 만세력 기반의 100% 정확한 간지 추출
- **LLM 호출 비용 절감**: 문장 DB 조합 및 캐싱으로 토큰 사용량 최소화
- **빠른 응답 속도**: 중복 계산을 배제한 아키텍처
- **데이터 캐싱 기반 구조**: 효율적인 리소스 관리

---

# 🏗️ System Architecture
## 시스템 전체 흐름

```text
User
 ↓
Frontend (React)
 ↓
FastAPI Backend
 ↓
Saju Calculation Engine
 ↓
PostgreSQL Database
 ↓
RAG (Vector Search / Fortune Phrases / Saju Docs)
 ↓
Prompt Builder
 ↓
LLM
 ↓
daily_fortunes 저장
 ↓
Push Notification
```

---

# 🧠 Core Architecture (이 프로젝트의 핵심 설계)
이 프로젝트의 핵심은 단순 운세 생성이 아니라 **LLM 기반 개인화 콘텐츠 생성 시스템 구조 설계**에 있습니다.

### 핵심 설계 포인트
1. **비회원 UUID 사용자 시스템**
   - 회원가입 없이 UUID로 사용자 식별 및 유효성 유지 (localStorage / Cookie)
2. **만세력 간지 캐싱 구조**
   - 생년월일 → 간지 계산 → `saju_profiles` 저장 (성능 최적화)
3. **AI 운세 생성 + 문장 DB 혼합 구조**
   - `fortune_phrases` DB와 AI 생성 문장 조합으로 토큰 비용 절감
4. **daily_fortunes UNIQUE 제약**
   - `UNIQUE (profile_id, target_date)`로 불필요한 AI 호출 원천 차단
5. **fortune_logs 기반 프롬프트 튜닝 구조**
   - AI 질문/답변 전수 저장으로 지속적인 프롬프트 엔지니어링 가능

---

# ✨ Key Features
| 기능 | 상세 설명 |
| :--- | :--- |
| **하이브리드 분석** | 만세력 정밀 계산 및 간지 데이터 DB 캐싱으로 즉시 응답 |
| **AI 운세 컨설팅** | 사주 원국 기반 개인화 운세 및 문장 DB 혼합 생성 |
| **개인화 사주 관리** | 본인/가족/친구 등 다중 프로필 저장 및 히스토리 조회 |
| **리텐션 및 운영** | FCM 푸시 알림 및 AI Prompt Logging을 통한 품질 관리 |

---

# 🗄️ Database Design
## 핵심 테이블 구조

```text
users
 ├── saju_profiles
 │       ├── daily_fortunes
 │       └── fortune_logs
 └── push_subscriptions

fortune_phrases (독립 마스터 테이블)
```

---

# 🛠️ Tech Stack
| 분류 | 기술 |
|------|------|
| Backend | Python, FastAPI |
| ORM | SQLAlchemy, Pydantic |
| Database | PostgreSQL |
| AI | LLM + RAG (Retrieval-Augmented Generation) |
| Vector Database | Chroma |
| Embeddings | Sentence Transformers |
| Frontend | React |
| Deployment | Docker |

---

# 📂 Project Structure
```text
AI-Saju-Master/
│
├── app/                         # 백엔드 애플리케이션
│    ├── api/                    # 라우터 / 컨트롤러
│    │    ├── user_router.py
│    │    ├── profile_router.py
│    │    ├── fortune_router.py
│    │    └── compatibility_router.py
│    │
│    ├── models/                 # DB 모델 (ORM)
│    │    ├── user.py
│    │    ├── profile.py
│    │    ├── saju.py
│    │    ├── fortune.py
│    │    └── fortune_log.py
│    │
│    ├── services/               # 비즈니스 로직
│    │    ├── saju_service.py
│    │    ├── fortune_service.py
│    │    ├── compatibility_service.py
│    │    └── llm_service.py
│    │
│    ├── db/                     # DB 설정
│    │    ├── database.py
│    │    └── session.py
│    │
│    ├── core/                   # 설정, 환경변수, 공통 로직
│    │    ├── config.py
│    │    └── security.py
│    │
│    └── main.py                 # FastAPI 진입점
│
├── docs/                        # 프로젝트 설계 문서
│    ├── 01_concept_and_requirements.md
│    ├── 02_service_flow.md
│    ├── 03_system_architecture.md
│    ├── 04_db_design.md
│    ├── 05_ai_logic.md
│    ├── 06_api_design.md
│    ├── 07_prompt_design.md
│    ├── 08_business_model.md
│    ├── 09_roadmap.md
│    └── 10_troubleshooting_log.md
│
├── erd/                         # ERD, 다이어그램
│    ├── saju_erd.png
│    └── architecture.png
│
├── prompts/                     # 프롬프트 관리
│    ├── daily_fortune_prompt.txt
│    ├── saju_analysis_prompt.txt
│    ├── compatibility_prompt.txt
│    └── system_prompt.txt
│
├── scripts/                     # 배치 / 크롤링 / 스케줄러
│    ├── generate_daily_fortune.py
│    └── data_preprocessing.py
│
├── tests/                       # 테스트 코드
│
├── .env
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
└── README.md
```

---

# 🎯 What I Learned
이 프로젝트를 통해 다음과 같은 아키텍처 설계 역량을 확보했습니다.
- **UUID 기반 비회원 사용자 시스템** 설계 및 유지 기법
- **만세력 간지 캐싱**을 통한 연산 부하 최적화
- **LLM 비용 절감을 위한 Hybrid 구조** (DB 문장 + AI 생성) 설계
- **PostgreSQL Unique 제약**을 활용한 비즈니스 비용 방어 및 데이터 무결성 관리
- **AI Prompt Logging**을 통한 LLM 튜닝 및 서비스 품질 개선 프로세스
- **개인화 콘텐츠 생성 서비스**의 엔드투엔드(End-to-End) 아키텍처 설계

---
# 📈 Changelog
| Version | Date | Description |
|:---:|:---:|:---|
| **v0.1** | 2026-03-30 | DB 설계 및 프로젝트 초기 구조 설계 완료 |
| **v0.2** | TBD | FastAPI API CRUD 구현 예정 |
| **v0.3** | TBD | LLM 운세 생성 및 문장 조합 로직 구현 예정 |
| **v0.4** | TBD | FCM Push 알림 기능 연동 예정 |
| **v1.0** | TBD | 전체 통합 테스트 및 최종 서비스 배포 |
---

# ⭐ Project Summary
> **AI 사주 Master는 단순 운세 생성 프로젝트가 아니라,  
> LLM 기반 개인화 콘텐츠 생성 시스템 아키텍처를 설계하고 구현하는 프로젝트입니다.**