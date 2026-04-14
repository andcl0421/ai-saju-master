# 📜 Domain Rules - AI 사주 Master

이 문서는 **AI 사주 Master** 시스템의 비즈니스 로직과 데이터 흐름의 절대 원칙을 정의합니다.  
모든 코드 생성, 데이터 처리, API 설계, 그리고 AI 해석 로직은 본 문서의 규칙을 최우선으로 준수해야 합니다.

---

## 1. 서비스 핵심 목표 (Service Objective)

AI 사주 Master는 이메일 기반의 간편한 사용자 식별 방식을 통해 **회원가입이나 이메일 인증 없이도** 누구나 즉시 사주 분석 서비스를 이용할 수 있도록 하는 것을 목표로 한다.

### 1.1 핵심 목표
- 사용자는 **이메일 입력만으로** 서비스를 즉시 이용할 수 있다.
- 이메일은 사용자 식별을 위한 **고유 식별자(Unique Identifier)**로 사용된다.
- 동일 이메일로 생성된 분석 이력은 **개인화된 해석**에 활용된다.
- 복잡한 로그인 절차 없이 **진입 장벽을 최소화**한다.
- 향후 필요 시 인증 기반 계정 시스템으로 **확장 가능**하도록 설계한다.

### 1.2 제공 기능
- 사주 팔자(연·월·일·시) 계산
- 오행 분석 및 시각화
- AI 기반 개인화 해석
- 분석 결과 저장 및 재조회
- 이메일 기반 사용자 이력 관리

---

## 2. 사용자 식별 규칙 (User Identification Rules)

### 2.1 사용자 개념
- 본 서비스는 회원(Member)과 비회원(Guest)을 구분하지 않는다.
- 모든 사용자는 이메일 주소를 기반으로 식별된다.

### 2.2 식별 방식
1. 사용자는 이메일 주소를 입력함으로써 서비스를 즉시 이용할 수 있다.
2. 이메일은 시스템 내에서 사용자 식별을 위한 **고유 키(Unique Identifier)**로 사용된다.
3. 동일한 이메일로 생성된 모든 사주 분석 데이터는 동일 사용자에 속한 것으로 간주한다.
4. 이메일 인증은 수행하지 않으며, 입력된 이메일의 소유 여부는 검증하지 않는다.
5. 향후 서비스 확장을 위해 인증 기반 계정 시스템으로 전환 가능하도록 설계한다.

### 2.3 사용자 데이터 관리
- 이메일은 `users` 테이블에서 **PRIMARY KEY**로 사용된다.
- 사용자의 모든 사주 분석 이력은 `user_email`을 통해 연결된다.
- `saju_profiles.user_email`은 `users.email`을 참조하는 **외래 키(Foreign Key)**이다.
- 사용자는 하나의 이메일로 여러 개의 사주 프로필을 가질 수 있다. (1:N 관계)
- 개인정보 보호를 위해 이메일은 필요 시 마스킹 또는 해싱하여 저장할 수 있다.

---

## 3. 데이터 변환 수칙 (Data Transformation Rules)

### 3.1 일반 원칙
1. 모든 사주 분석 요청은 이메일 주소를 기준으로 사용자와 연결된다.
2. 입력 데이터는 만세력 계산을 위해 **표준화된 형식**으로 변환되어야 한다.
3. 시스템은 계산에 사용된 값을 명확히 기록하여 **재현성(Reproducibility)**을 보장해야 한다.

### 3.2 생시(Birth Time) 처리 규칙
1. `birth_time`은 `VARCHAR(10)` 타입으로 저장된다.
2. 사용자가 생시를 모를 경우 기본값으로 `'UNKNOWN'`을 사용한다.
3. `birth_time = 'UNKNOWN'`인 경우:
   - 만세력 계산 시 내부적으로 **12:00(정오)**를 기준으로 시주를 산출한다.
   - 계산된 결과는 `time_ganji` 컬럼에 캐싱된다.
4. AI 해석 단계에서는 시주의 신뢰도를 낮추고 **삼주(연·월·일) 중심의 해석**을 수행한다.

### 3.3 날짜 및 시간 표준화
- `birth_date`: `YYYY-MM-DD` 형식의 ISO 8601 표준을 사용한다.
- 모든 시간 데이터는 **한국 표준시(KST, UTC+9)** 기준으로 처리한다.
- 성별은 `ENUM('MALE', 'FEMALE')` 값을 사용한다.

### 3.4 간지 데이터 캐싱 규칙
- 만세력 계산 결과는 다음 컬럼에 캐싱된다.
  - `year_ganji`
  - `month_ganji`
  - `day_ganji`
  - `time_ganji`
- 캐싱된 데이터는 동일한 요청에 대한 재계산을 방지하여 시스템 성능을 향상시킨다.

---

## 4. 만세력 엔진 규칙 (Mansae Calendar Engine)

### 4.1 입력(Input)

| 필드명 | 타입 | 설명 |
|-------|------|------|
| email | String | 사용자 식별자 |
| nickname | String | 프로필 별명 |
| birth_date | Date | 생년월일 |
| birth_time | String | 태어난 시간 (`HH:MM` 또는 `'UNKNOWN'`) |
| gender | ENUM | `MALE`, `FEMALE` |
| calendar_type | String | `solar` 또는 `lunar` |

### 4.2 출력(Output)

```json
{
  "year_ganji": "갑자",
  "month_ganji": "을축",
  "day_ganji": "병인",
  "time_ganji": "정묘",
  "five_elements": {
    "wood": 2,
    "fire": 1,
    "earth": 1,
    "metal": 2,
    "water": 2
  },
  "calculated_birth_time": "12:00",
  "is_time_unknown": true
}
```

---

## 5. Inference (AI) 규칙

### 5.1 아키텍처 개요
본 시스템은 **RAG(Retrieval-Augmented Generation)** 방식이 아닌,  
**FastAPI와 OpenAPI 스키마를 기반으로 한 OpenAI Function Calling 아키텍처**를 사용한다.

### 5.2 동작 방식
1. 사용자의 입력 데이터는 FastAPI 기반의 백엔드로 전달된다.
2. 만세력 엔진이 사주 팔자 및 오행 데이터를 계산한다.
3. 해당 기능들은 OpenAPI 스키마를 통해 LLM에 **함수(Function)** 형태로 제공된다.
4. LLM은 필요한 정보를 자율적으로 호출(Function Calling)하여 해석을 생성한다.
5. 동일 이메일로 생성된 과거 분석 이력은 추가적인 함수 호출을 통해 개인화된 해석에 활용될 수 있다.
6. `birth_time = 'UNKNOWN'`인 경우 시주 해석의 비중을 낮추거나 제외하도록 프롬프트에 반영한다.

### 5.3 Function Calling 예시

```json
{
  "name": "calculate_saju",
  "description": "사용자의 생년월일과 생시를 기반으로 사주 팔자를 계산한다.",
  "parameters": {
    "type": "object",
    "properties": {
      "birth_date": { "type": "string", "format": "date" },
      "birth_time": { "type": "string", "description": "HH:MM 또는 'UNKNOWN'" },
      "gender": { "type": "string", "enum": ["MALE", "FEMALE"] }
    },
    "required": ["birth_date", "birth_time", "gender"]
  }
}
```

---

## 6. 데이터베이스 설계 원칙 (Database Design Principles)

### 6.1 Users 테이블
```sql
CREATE TABLE users (
    email VARCHAR(100) PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL
);
```

### 6.2 Saju Profiles 테이블
```sql
CREATE TABLE saju_profiles (
    profile_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_email VARCHAR(100) NOT NULL,
    nickname VARCHAR(50) NOT NULL,
    birth_date DATE NOT NULL,
    birth_time VARCHAR(10) NOT NULL DEFAULT 'UNKNOWN',
    gender ENUM('MALE', 'FEMALE') NOT NULL,
    year_ganji VARCHAR(10),
    month_ganji VARCHAR(10),
    day_ganji VARCHAR(10),
    time_ganji VARCHAR(10),
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_email) REFERENCES users(email)
);
```

---

## 7. 보안 및 개인정보 보호 원칙

1. 이메일은 사용자 식별을 위한 최소한의 정보로만 수집한다.
2. 모든 API 통신은 HTTPS를 사용해야 한다.
3. 사용자의 요청이 있을 경우 관련 데이터는 삭제될 수 있어야 한다.
4. 개인정보 보호 관련 법규(예: 개인정보 보호법)를 준수한다.
5. 로그 및 분석 데이터에는 불필요한 개인정보를 저장하지 않는다.

---

## 8. 확장성 및 향후 고려 사항

- 이메일 인증 기반 로그인 시스템으로의 확장
- 소셜 로그인(Google, Apple 등) 연동
- 결제 및 구독 모델 추가
- 푸시 알림(`push_subscriptions`) 기능 확장
- 다국어 지원 및 글로벌 서비스 확장

---

## 9. 용어 정의 (Glossary)

| 용어 | 정의 |
|------|------|
| 사주 팔자 | 연, 월, 일, 시의 천간과 지지로 구성된 8개의 글자 |
| 천간 | 갑, 을, 병, 정, 무, 기, 경, 신, 임, 계 |
| 지지 | 자, 축, 인, 묘, 진, 사, 오, 미, 신, 유, 술, 해 |
| 오행 | 목(木), 화(火), 토(土), 금(金), 수(水) |
| 만세력 | 사주 팔자를 계산하기 위한 달력 시스템 |
| Function Calling | LLM이 외부 API를 함수 형태로 호출하는 방식 |

---

## 📌 부칙

- 본 문서는 AI 사주 Master 시스템의 **최상위 도메인 규칙**으로 간주된다.
- 모든 개발자는 본 문서를 기준으로 설계 및 구현을 수행해야 한다.
- 문서의 변경 사항은 버전 관리를 통해 추적되어야 한다.

**Version:** 1.1  
**Last Updated:** 2026-04-09