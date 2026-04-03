# 📂 04_db_design.md (Final) - 데이터베이스 설계서

## 1. 개요 (Introduction)
본 문서는 '만세력 AI 서비스'의 데이터 구조를 정의한다.  
이메일 기반 사용자 식별 구조를 채택하여 확장성, 성능, 그리고 AI 비용 최적화에 초점을 맞추어 설계되었다.

---

## 2. 설계 원칙 (Design Principles)
* **Identity**: 이메일 기반 사용자 식별을 통한 계정 관리 및 데이터 복구 기능 제공.
* **Performance**: 사주 간지(Ganji) 데이터를 프로필에 캐싱하여 AI 추론 속도 향상.
* **Cost-Efficiency**: 문장 재료(`fortune_phrases`) 테이블을 활용한 조립식 운세 생성으로 LLM 토큰 비용 절감.
* **Reliability**: 날짜별 결과 저장 및 상세 로그 기록을 통한 데이터 일관성 유지.

---

## 3. 테이블 상세 설계

### ① `users` (사용자 계정)
| 컬럼명 | 타입 | 제약 조건 | 설명 |
| :--- | :--- | :--- | :--- |
| **user_id** | INT | PK, AUTO_INCREMENT | 사용자 고유 식별자 |
| **email** | VARCHAR(100) | UNIQUE, NOT NULL | 사용자 이메일 (계정 식별용) |
| **created_at** | TIMESTAMP | DEFAULT NOW() | 계정 생성 일시 |
| **last_login** | TIMESTAMP | - | 최근 접속 일시 |

---

### ② `saju_profiles` (사주 정보)
| 컬럼명 | 타입 | 제약 조건 | 설명 |
| :--- | :--- | :--- | :--- |
| **profile_id** | BIGINT | PK, AUTO_INCREMENT | 프로필 고유 번호 |
| **user_id** | INT | FK (users.user_id) | 사용자 계정 연결 |
| **nickname** | VARCHAR(50) | NOT NULL | 별명 (나, 가족, 친구 등) |
| **birth_date** | DATE | NOT NULL | 생년월일 |
| **birth_time** | VARCHAR(10) | - | 태어난 시간 ('00:00' 또는 '모름') |
| **gender** | ENUM | 'MALE', 'FEMALE' | 성별 |
| **calendar_type** | ENUM | 'SOLAR', 'LUNAR' | 양력/음력 구분 |
| **year_ganji** | VARCHAR(10) | - | [캐싱] 연 간지 |
| **month_ganji** | VARCHAR(10) | - | [캐싱] 월 간지 |
| **day_ganji** | VARCHAR(10) | - | [캐싱] 일 간지 |
| **time_ganji** | VARCHAR(10) | - | [캐싱] 시 간지 |
| **is_primary** | BOOLEAN | DEFAULT FALSE | 대표 프로필 여부 (푸시 대상) |

---

### ③ `daily_fortunes` (오늘의 운세 결과)
| 컬럼명 | 타입 | 제약 조건 | 설명 |
| :--- | :--- | :--- | :--- |
| **fortune_id** | BIGINT | PK, AUTO_INCREMENT | 운세 고유 ID |
| **profile_id** | BIGINT | FK (saju_profiles.profile_id) | 해당 사주 프로필 연결 |
| **target_date** | DATE | NOT NULL | 운세 날짜 |
| **fortune_score** | INT | 0~100 | 종합 운세 점수 |
| **money_score** | INT | 0~100 | 재물운 세부 점수 |
| **love_score** | INT | 0~100 | 연애운 세부 점수 |
| **health_score** | INT | 0~100 | 건강운 세부 점수 |
| **work_score** | INT | 0~100 | 직장/학업운 세부 점수 |
| **content** | TEXT | NOT NULL | 최종 운세 본문 |
| **luck_item** | VARCHAR(100) | - | 오늘의 행운 아이템 |
| **created_at** | TIMESTAMP | DEFAULT NOW() | 데이터 생성 시점 |

> **Constraint**: `UNIQUE (profile_id, target_date)` - 중복 생성 방지

---

### ④ `fortune_phrases` (운세 문장 재료)
| 컬럼명 | 타입 | 제약 조건 | 설명 |
| :--- | :--- | :--- | :--- |
| **phrase_id** | BIGINT | PK | 문구 고유 ID |
| **category** | VARCHAR(20) | - | 카테고리 |
| **mood** | VARCHAR(10) | - | 분위기 |
| **content** | TEXT | NOT NULL | 실제 문구 내용 |

---

### ⑤ `push_subscriptions` (푸시 알림 설정)
| 컬럼명 | 타입 | 제약 조건 | 설명 |
| :--- | :--- | :--- | :--- |
| **sub_id** | BIGINT | PK | 구독 고유 ID |
| **user_id** | INT | FK (users.user_id) | 사용자 계정 연결 |
| **fcm_token** | VARCHAR(255) | UNIQUE | 기기 고유 토큰 |
| **is_active** | BOOLEAN | DEFAULT TRUE | 알림 활성 여부 |
| **created_at** | TIMESTAMP | DEFAULT NOW() | 구독 등록 일시 |

---

### ⑥ `fortune_logs` (AI 추론 로그)
| 컬럼명 | 타입 | 제약 조건 | 설명 |
| :--- | :--- | :--- | :--- |
| **log_id** | BIGINT | PK | 로그 고유 ID |
| **profile_id** | BIGINT | FK (saju_profiles.profile_id) | 요청 사주 정보 연결 |
| **prompt** | TEXT | - | AI에게 보낸 프롬프트 |
| **response** | TEXT | - | AI 응답 원문 |
| **target_date** | DATE | - | 기록 대상 날짜 |
| **created_at** | TIMESTAMP | DEFAULT NOW() | 로그 생성 일시 |

---

## 4. 인덱스(Index) 설계
* `idx_users_email`: `users(email)`
* `idx_profiles_user`: `saju_profiles(user_id)`
* `idx_fortunes_date`: `daily_fortunes(target_date)`
* `idx_push_user`: `push_subscriptions(user_id)`
* `UNIQUE (profile_id, target_date)`