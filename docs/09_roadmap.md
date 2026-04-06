# 📂 09_roadmap.md (v1.3 Final)
## 프로젝트 로드맵 (Project Roadmap)

---

## 1. 개요 (Overview)
본 문서는 '만세력 AI 서비스'의 개발 단계별 일정과 주요 마일스톤, 그리고 정식 출시 이후의 기능 고도화 계획을 정의한다. 개발은 MVP(최소 기능 제품) → 고도화 → 수익화 단계 순서로 진행한다.

---

## 2. 개발 단계별 마일스톤 (Milestones)

### Phase 1: 서비스 설계 및 환경 구축 (Architecture & Setup)
- [x] 서비스 기획 및 요구사항 정의 (`01_concept.md`)
- [x] 서비스 흐름 설계 (`02_service_flow.md`)
- [x] 시스템 아키텍처 설계 (`03_system_architecture.md`)
- [x] 데이터베이스 모델링 (`04_db_modeling.md`)
- [x] API 설계 (`06_api_design.md`)
- [x] 프롬프트 설계 (`07_prompt_design.md`)
- [x] 개발 환경 구축 (FastAPI, PostgreSQL, Docker)

### Phase 2: 사주 계산 엔진 및 프로필 시스템 (Saju Calculation Engine)
- [ ] 만세력 라이브러리 연동 (Python k_lunar 등)
- [ ] 생년월일 → 간지(년주/월주/일주/시주) 계산 로직 구현
- [ ] 오행(목, 화, 토, 금, 수) 계산 로직 구현
- [ ] `saju_profiles` 생성 및 조회 API 구현

### Phase 3: AI 운세 생성 시스템 (LLM Fortune Generation)
- [ ] 오늘의 운세 Prompt 파이프라인 구현 (`07_prompt_design.md` 준수)
- [ ] LLM(GPT) API 연동 및 JSON 응답 파싱/Validation
- [ ] 운세 결과 `daily_fortunes` 테이블 저장 및 캐싱 로직 (하루 1회 생성 제한)

### Phase 4: API 서버 완성 (Backend API Development)
- [ ] User API 및 Profile API 고도화
- [ ] Daily Fortune & Compatibility(궁합) API 구현
- [ ] 이메일 기반 인증(Auth) 시스템 연동
- [ ] 전체 엔드포인트 단위 테스트(Unit Test)

### Phase 5: 프론트엔드 개발 및 연동 (Frontend Integration)
- [ ] React UI 개발 (Tailwind CSS 활용)
- [ ] 사주 입력, 프로필 관리, 운세/궁합 결과 화면 구현
- [ ] API 연동 (Axios 활용) 및 상태 관리

### Phase 6: 배포 및 운영 (Deployment & Production)
- [ ] AWS EC2/RDS 인프라 구축 및 Docker 배포
- [ ] 도메인 연결 및 SSL(HTTPS) 설정
- [ ] AI API 비용 모니터링 및 로그 수집 설정

---

## 3. 서비스 고도화 단계 (Future Updates)

### v1.5: 기능 고도화
- Vector DB 기반 RAG 시스템 구축 (명리학 지식 정교화)
- '오늘의 운세 카드' 이미지 생성 및 SNS 공유 기능
- 소셜 로그인 (카카오 / 네이버) 연동

### v2.0: 서비스 확장
- AI 관상 분석 (Vision 모델) 및 타로 카드 기능 추가
- 월간/연간 운세 프리미엄 리포트 출시
- 구독 및 결제 시스템 도입

### v3.0: 플랫폼화
- B2B 운세 API 유료 제공 및 다국어 지원 (글로벌 확장)

---

## 4. 위험 관리 (Risk Management)
- **비용 관리**: 운세 캐싱 및 저비용 모델(GPT-4o mini) 혼합 사용
- **정확도 보완**: 명리학 전문가 검수를 통한 RAG 데이터셋 지속 보완
- **안정성 확보**: 비동기 처리(Celery 등) 도입 검토 및 실시간 모니터링

---

## 5. 전체 개발 흐름 요약 (Development Flow)
```
DB 설계 → 사주 계산 로직 → 프로필 API → 운세 생성 AI → API 서버 완성 → 프론트엔드 → 배포 → RAG 고도화 → 수익화
```