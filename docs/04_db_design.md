# 📂 04_db_design.md (Final) - 데이터베이스 설계서

## 1. 개요 (Introduction)
본 문서는 '만세력 AI 서비스'의 데이터 구조를 정의한다.  
**이메일(Email) 기반 사용자 식별 구조**를 채택하여 단순성, 성능, 그리고 데이터 일관성에 초점을 맞추어 설계되었다.

---

## 2. 설계 원칙 (Design Principles)
* **Email Identity**: UUID 대신 이메일을 사용자 식별자로 사용하여 조인(Join) 구조를 단순화.
* **Performance**: 사주 간지(Ganji) 데이터를 프로필 테이블에 캐싱하여 만세력 계산 부하 최소화.
* **Cost-Efficiency**: 문구 조합(`fortune_phrases`) 방식으로 LLM 토큰 사용량 최적화.
* **Reliability**: `UNIQUE (profile_id, target_date)` 제약으로 하루 1회 운세 생성 보장.

---

## 3. 테이블 상세 설계

### ① users (사용자 계정)
- **존재 이유**: 서비스 이용자 식별 및 로그인 연동을 위한 기초 데이터 관리
- **관계성**: 1:N (saju_profiles, push_subscriptions)

| 구분 | 컬럼명 | 역할 | 타입/옵션 | 출처 | 비고 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **PK** | **email** | 사용자 이메일 | VARCHAR(100), N | 소셜 연동 | 유일 식별자 |
| **일반** | **created_at** | 가입 일시 | TIMESTAMP, N | 시스템 | Server Default: CURRENT_TIMESTAMP |
| **일반** | **last_login** | 최근 접속 일시 | TIMESTAMP, Y | 시스템 | 최근 활동 추적용 |

---

### ② saju_profiles (사주 정보)
- **존재 이유**: 사용자별 사주 정보를 저장하고 간지 데이터를 캐싱하여 계산 부하 감소
- **관계성**: N:1 (users), 1:N (daily_fortunes, fortune_logs)

| 구분 | 컬럼명 | 역할 | 타입/옵션 | 출처 | 비고 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **PK** | **profile_id** | 프로필 식별자 | BIGINT, N | 시스템 | Auto Increment |
| **FK** | **user_email** | 사용자 연결 | VARCHAR(100), N | 시스템 | users.email 참조 |
| **일반** | **nickname** | 활동명(별명) | VARCHAR(50), N | 사용자 입력 | 나, 가족, 친구 등 구분 |
| **일반** | **birth_date** | 생년월일 | DATE, N | 사용자 입력 | - |
| **일반** | **birth_time** | 태어난 시간 | VARCHAR(10), N | 사용자 입력 | 기본값: 'UNKNOWN' |
| **일반** | **gender** | 성별 | ENUM, N | 사용자 입력 | MALE, FEMALE |
| **일반** | **year_ganji** | 연 간지 | VARCHAR(10), Y | 시스템 | [캐싱] 만세력 계산 결과 |
| **일반** | **month_ganji** | 월 간지 | VARCHAR(10), Y | 시스템 | [캐싱] 만세력 계산 결과 |
| **일반** | **day_ganji** | 일 간지 | VARCHAR(10), Y | 시스템 | [캐싱] 만세력 계산 결과 |
| **일반** | **time_ganji** | 시 간지 | VARCHAR(10), Y | 시스템 | [캐싱] 만세력 계산 결과 |
| **일반** | **is_primary** | 대표 프로필 여부 | BOOLEAN, N | 사용자 입력 | 기본값: False (푸시 알림 대상) |

---

### ③ daily_fortunes (오늘의 운세 결과)
- **존재 이유**: 생성된 일일 운세 결과값 저장 및 중복 생성 방지
- **관계성**: N:1 (saju_profiles)

| 구분 | 컬럼명 | 역할 | 타입/옵션 | 출처 | 비고 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **PK** | **fortune_id** | 운세 고유 ID | BIGINT, N | 시스템 | Auto Increment |
| **FK** | **profile_id** | 프로필 연결 | BIGINT, N | 시스템 | saju_profiles.profile_id 참조 |
| **일반** | **target_date** | 운세 날짜 | DATE, N | 시스템 | Unique Index (profile_id와 조합) |
| **일반** | **fortune_score** | 종합 점수 | INT, N | 시스템 | 0~100 |
| **일반** | **money_score** | 재물운 점수 | INT, N | 시스템 | 0~100 |
| **일반** | **love_score** | 연애운 점수 | INT, N | 시스템 | 0~100 |
| **일반** | **health_score** | 건강운 점수 | INT, N | 시스템 | 0~100 |
| **일반** | **work_score** | 학업/직장 점수 | INT, N | 시스템 | 0~100 |
| **일반** | **content** | 운세 본문 | TEXT, N | 시스템 | 최종 생성 텍스트 |
| **일반** | **luck_item** | 행운 아이템 | VARCHAR(100), Y | 시스템 | 추천 아이템 |
| **일반** | **created_at** | 생성 시점 | TIMESTAMP, N | 시스템 | Default: CURRENT_TIMESTAMP |

> **Constraint**: `UNIQUE (profile_id, target_date)` 적용

---

### ④ fortune_phrases (운세 문장 재료)
- **존재 이유**: LLM 비용 절감 및 일관된 톤앤매너 유지를 위한 조립식 문구 관리

| 구분 | 컬럼명 | 역할 | 타입/옵션 | 출처 | 비고 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **PK** | **phrase_id** | 문구 고유 ID | BIGINT, N | 시스템 | - |
| **일반** | **category** | 문구 카테고리 | VARCHAR(20), N | 운영자 | 인사말, 재물운, 연애운 등 |
| **일반** | **mood** | 분위기 상태 | VARCHAR(10), N | 운영자 | 긍정, 보통, 주의 |
| **일반** | **content** | 실제 문구 내용 | TEXT, N | 운영자 | {name} 등 치환자 포함 가능 |

---

### ⑤ push_subscriptions (푸시 알림 설정)
- **존재 이유**: 사용자의 기기별 알림 수신 상태 및 토큰 관리 (추후 구현 예정)

| 구분 | 컬럼명 | 역할 | 타입/옵션 | 출처 | 비고 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **PK** | **sub_id** | 구독 고유 ID | BIGINT, N | 시스템 | - |
| **FK** | **user_email** | 사용자 연결 | VARCHAR(100), N | 시스템 | users.email 참조 |
| **일반** | **fcm_token** | 기기 토큰 | VARCHAR(255), N | 시스템 | Unique |
| **일반** | **is_active** | 알림 활성 여부 | BOOLEAN, N | 사용자 설정 | 기본값: True |
| **일반** | **created_at** | 구독 등록 일시 | TIMESTAMP, N | 시스템 | Default: NOW() |

---

### ⑥ fortune_logs (AI 추론 로그)
- **존재 이유**: AI 응답 품질 모니터링 및 트러블슈팅을 위한 기록 보관

| 구분 | 컬럼명 | 역할 | 타입/옵션 | 출처 | 비고 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **PK** | **log_id** | 로그 고유 ID | BIGINT, N | 시스템 | - |
| **FK** | **profile_id** | 사주 정보 연결 | BIGINT, N | 시스템 | saju_profiles.profile_id 참조 |
| **일반** | **prompt** | 요청 프롬프트 | TEXT, Y | 시스템 | AI 전송 데이터 |
| **일반** | **response** | 응답 원문 | TEXT, Y | 시스템 | AI 수신 데이터 |
| **일반** | **target_date** | 기록 대상 날짜 | DATE, Y | 시스템 | 운세 기준일 |
| **일반** | **created_at** | 로그 생성 일시 | TIMESTAMP, N | 시스템 | Default: NOW() |

---

## 4. 구현 시 주의사항 (Implementation Notes)
* **Time Handling**: `birth_time`이 입력되지 않은 경우, 애플리케이션 로직에서 `None` 대신 `'UNKNOWN'` 문자열을 삽입한다.
* **Initial Data**: `fortune_phrases` 테이블에는 서비스 가동 전 기초 운세 조각 데이터를 최소 20개 이상 Pre-load 해야 한다.

---

## 5. 인덱스(Index) 설계
* `idx_profiles_email`: `saju_profiles(user_email)` - 사용자별 프로필 조회 최적화
* `idx_fortunes_lookup`: `UNIQUE (profile_id, target_date)` - 일일 운세 조회 및 중복 방지
* `idx_push_email`: `push_subscriptions(user_email)` - 알림 대상자 조회 최적화