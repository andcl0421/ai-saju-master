````md
# 📂 06_database_schema.md
## 만세력 AI 서비스 데이터베이스 스키마 (Final)

---

## 1. Users (사용자 계정)
가장 기본이 되는 사용자 테이블이며 이메일을 ID로 사용한다.

```sql
CREATE TABLE IF NOT EXISTS users (
    email       VARCHAR(100) PRIMARY KEY, -- 사용자 식별자
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login  TIMESTAMP                 -- 마지막 로그인 시간
);
```

---

## 2. Saju Profiles (사주 프로필)
사용자 한 명이 여러 개의 사주 프로필을 가질 수 있다.

```sql
CREATE TABLE IF NOT EXISTS saju_profiles (
    profile_id     BIGSERIAL PRIMARY KEY,
    user_email     VARCHAR(100) NOT NULL,
    nickname       VARCHAR(50)  NOT NULL,
    birth_date     DATE         NOT NULL,
    birth_time     VARCHAR(10)  DEFAULT 'UNKNOWN', -- '14:30'
    gender         VARCHAR(10)  CHECK (gender IN ('MALE', 'FEMALE')),
    calendar_type  VARCHAR(10)  CHECK (calendar_type IN ('SOLAR', 'LUNAR')),
    
    -- 만세력 계산 결과 캐싱
    year_ganji     VARCHAR(10),
    month_ganji    VARCHAR(10),
    day_ganji      VARCHAR(10),
    time_ganji     VARCHAR(10),
    
    is_primary     BOOLEAN   DEFAULT FALSE,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_user_email 
        FOREIGN KEY (user_email)
        REFERENCES users(email)
        ON DELETE CASCADE
);
```

---

## 3. Daily Fortunes (오늘의 운세)
하루에 프로필당 1개의 운세만 생성되도록 UNIQUE 제약을 둔다.

```sql
CREATE TABLE IF NOT EXISTS daily_fortunes (
    fortune_id     BIGSERIAL PRIMARY KEY,
    profile_id     BIGINT    NOT NULL,
    target_date    DATE      NOT NULL,
    
    -- 점수 시스템
    fortune_score  INT CHECK (fortune_score BETWEEN 0 AND 100),
    money_score    INT CHECK (money_score BETWEEN 0 AND 100),
    love_score     INT CHECK (love_score BETWEEN 0 AND 100),
    health_score   INT CHECK (health_score BETWEEN 0 AND 100),
    work_score     INT CHECK (work_score BETWEEN 0 AND 100),
    
    content        TEXT      NOT NULL,
    luck_item      VARCHAR(100),
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 하루 1운세 제한
    CONSTRAINT unique_fortune_per_day UNIQUE (profile_id, target_date),
    CONSTRAINT fk_profile_id 
        FOREIGN KEY (profile_id)
        REFERENCES saju_profiles(profile_id)
        ON DELETE CASCADE
);
```

---

## 4. Fortune Phrases (운세 문장 템플릿)
AI 운세 문장 생성을 위한 템플릿 저장 테이블.

```sql
CREATE TABLE IF NOT EXISTS fortune_phrases (
    phrase_id  BIGSERIAL PRIMARY KEY,
    category   VARCHAR(20) NOT NULL, -- 재물, 연애, 건강, 직장
    mood       VARCHAR(10) NOT NULL, -- GOOD, NORMAL, BAD
    content    TEXT        NOT NULL
);
```

---

## 5. Fortune Logs (AI 사용 로그)
AI 호출 로그 및 비용 추적, 디버깅용 테이블.

```sql
CREATE TABLE IF NOT EXISTS fortune_logs (
    log_id      BIGSERIAL PRIMARY KEY,
    user_email  VARCHAR(100),
    profile_id  BIGINT,
    prompt      TEXT,
    response    TEXT,
    token_usage INT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 6. Push Subscriptions (푸시 알림)
푸시 알림을 위한 FCM 토큰 저장 테이블.

```sql
CREATE TABLE IF NOT EXISTS push_subscriptions (
    sub_id      BIGSERIAL PRIMARY KEY,
    user_email  VARCHAR(100) NOT NULL,
    fcm_token   VARCHAR(255) UNIQUE NOT NULL,
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_push_user_email 
        FOREIGN KEY (user_email)
        REFERENCES users(email)
        ON DELETE CASCADE
);
```

---

## 7. Index (조회 성능 최적화)

```sql
CREATE INDEX IF NOT EXISTS idx_profiles_user_email 
ON saju_profiles(user_email);

CREATE INDEX IF NOT EXISTS idx_fortunes_lookup 
ON daily_fortunes(profile_id, target_date);

CREATE INDEX IF NOT EXISTS idx_logs_user 
ON fortune_logs(user_email);
```

---

## 8. ERD 구조 관계

```
users
 └── saju_profiles
        ├── daily_fortunes
        ├── fortune_logs
        └── (future) compatibility

users
 └── push_subscriptions
```

---

## 9. 전체 테이블 구조 요약

| Table | Description |
|------|-------------|
| users | 사용자 계정 |
| saju_profiles | 사주 프로필 |
| daily_fortunes | 오늘의 운세 |
| fortune_phrases | 운세 문장 템플릿 |
| fortune_logs | AI 로그 / 비용 |
| push_subscriptions | 푸시 알림 |

---

## 10. 서비스 데이터 흐름 구조

```
User → Profiles → Daily Fortunes
                 → Fortune Logs
                 → Compatibility (Future)
User → Push Subscriptions
```

---
````
