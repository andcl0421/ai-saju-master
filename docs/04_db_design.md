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

### ① `users` (사용자 계정)
| 컬럼명 | 타입 | 제약 조건 | 설명 |
| :--- | :--- | :--- | :--- |
| **email** | VARCHAR(100) | **PK** | 사용자 이메일 (유일 식별자) |
| **created_at** | TIMESTAMP | DEFAULT NOW() | 계정 생성 일시 |
| **last_login** | TIMESTAMP | - | 최근 접속 일시 |

### ② `saju_profiles` (사주 정보)
| 컬럼명 | 타입 | 제약 조건 | 설명 |
| :--- | :--- | :--- | :--- |
| **profile_id** | BIGINT | PK, AUTO_INCREMENT | 프로필 고유 번호 |
| **user_email** | VARCHAR(100) | **FK (users.email)** | 사용자 계정(이메일) 연결 |
| **nickname** | VARCHAR(50) | NOT NULL | 별명 (나, 가족, 친구 등) |
| **birth_date** | DATE | NOT NULL | 생년월일 |
| **birth_time** | VARCHAR(10) | **DEFAULT 'UNKNOWN'** | 태어난 시간 ('00:00' 또는 'UNKNOWN') |
| **gender** | ENUM | 'MALE', 'FEMALE' | 성별 |
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
| **category** | VARCHAR(20) | - | 인사말,재물운,연애운 등 |
| **mood** | VARCHAR(10) | - | 분위기(긍정,보통,주의) |
| **content** | TEXT | NOT NULL | 실제 문구 내용 |

---

### ⑤ `push_subscriptions` (푸시 알림 설정)[추후 구현 예정]
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

## 4. 구현 시 주의사항 (Implementation Notes)
* **Time Handling**: `birth_time`이 입력되지 않은 경우, 애플리케이션 로직에서 `None` 대신 `'UNKNOWN'` 문자열을 삽입한다.
* **Initial Data**: `fortune_phrases` 테이블에는 서비스 가동 전 기초 운세 조각 데이터를 최소 20개 이상 Pre-load 해야 한다.

---

## 5. 인덱스(Index) 설계
* `idx_profiles_email`: `saju_profiles(user_email)`
* `idx_fortunes_lookup`: `UNIQUE (profile_id, target_date)`
* `idx_push_email`: `push_subscriptions(user_email)`