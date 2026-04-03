# 📂 05_api_design.md (v1.2) - API 상세 설계서

## 1. 개요
본 문서는 '만세력 AI 서비스'의 프론트엔드와 백엔드 서버 간 데이터 통신 규격을 정의한다.  
모든 API는 **RESTful** 방식으로 설계되며, JSON 형식으로 데이터를 주고받는다.

- **Base URL**: `/api/v1`
- **Version**: 1.2 (REST 구조 및 로직 명확화 반영)

---

## 2. 공통 응답 형식
모든 API 응답은 일관된 JSON 구조를 유지하여 클라이언트의 예외 처리를 돕는다.

### 성공 응답 (Success)
```json
{
  "status": "success",
  "data": { }
}
```

### 실패 응답 (Error)
```json
{
  "status": "error",
  "message": "상세 에러 메시지 내용"
}
```

---

## 3. Users API (사용자 인증)

### 3.1 사용자 생성 및 로그인
이메일을 기반으로 사용자를 식별하며, 최초 접속 시 계정을 생성한다.

- **Endpoint**: `POST /api/v1/users`
- **Request Body**:
```json
{
  "email": "user@example.com"
}
```

- **Response Data**: `user_id`, `email`, `last_login`

- **Logic**:
1. `users` 테이블에서 이메일 존재 여부 확인.
2. 존재 시 `last_login` 업데이트 후 반환.
3. 미존재 시 신규 사용자 생성.
4. `user_id` 반환.

---

## 4. Profiles API (사주 프로필 관리)

### 4.1 프로필 생성 (Create)
생년월일시 정보를 입력받아 서버에서 간지를 계산하고 캐싱 저장한다.

- **Endpoint**: `POST /api/v1/profiles`
- **Request Body**:
```json
{
  "user_id": 1,
  "nickname": "나",
  "birth_date": "1995-03-31",
  "birth_time": "14:30",
  "calendar_type": "SOLAR",
  "gender": "MALE"
}
```

- **Response Data**: `profile_id`

- **Logic**:
1. 생년월일시 입력 데이터 수신
2. 만세력 라이브러리 실행
3. 4주 8자 간지(year, month, day, time) 계산
4. `saju_profiles` 테이블 저장

---

### 4.2 프로필 목록 조회 (List)
사용자의 프로필 목록을 조회한다.

- **Endpoint**:
```
GET /api/v1/users/{user_id}/profiles
```

- **Response Data**:
프로필 ID, 닉네임, 대표 프로필 여부 목록 반환

---

### 4.3 대표 프로필 설정 (Set Primary)
푸시 알림 및 기본 운세 기준이 되는 대표 프로필을 설정한다.

- **Endpoint**:
```
PUT /api/v1/profiles/{profile_id}/primary
```

- **Logic**:
1. 요청된 profile_id의 `is_primary = true`
2. 동일 user_id의 기존 `is_primary = true` 프로필은 모두 `false`로 업데이트
3. 한 사용자당 대표 프로필은 1개만 존재

---

### 4.4 프로필 삭제 (Delete)
- **Endpoint**:
```
DELETE /api/v1/profiles/{profile_id}
```

---

## 5. Fortune API (오늘의 운세)

### 5.1 오늘의 운세 조회
- **Endpoint**:
```
GET /api/v1/fortunes/today/{profile_id}
```

- **Response Data**:
운세 점수(0~100), 운세 본문, 행운 아이템

- **Logic**:
1. 서버 기준 오늘 날짜를 `target_date`로 설정
2. `daily_fortunes` 테이블에서  
   `(profile_id, target_date)` 데이터 조회
3. **Cache Hit** → DB 데이터 반환
4. **Cache Miss** → Hybrid AI 로직 실행
5. AI 운세 생성 결과를 DB 저장
6. 사용자에게 결과 반환

---

## 6. Compatibility API (인연 궁합)

### 6.1 실시간 궁합 분석
두 프로필 간의 사주 조화를 분석한다. 결과는 저장하지 않는 실시간 분석 데이터다.

- **Endpoint**:
```
POST /api/v1/compatibility
```

- **Request Body**:
```json
{
  "profile_id_a": 1,
  "profile_id_b": 2
}
```

- **Logic**:
1. 두 프로필의 간지 데이터(year, month, day, time)를 조회
2. 간지 데이터를 LLM 입력 프롬프트로 전달
3. AI 궁합 분석 실행
4. 점수, 관계 유형, 요약, 조언 생성
5. 결과 반환 (DB 저장하지 않음)

---

## 7. Push API (알림 설정)

### 7.1 FCM 토큰 등록
푸시 알림을 위해 사용자의 디바이스 토큰을 저장한다.

- **Endpoint**:
```
POST /api/v1/push/register
```

- **Request Body**:
```json
{
  "user_id": 1,
  "fcm_token": "token_string"
}
```

- **Logic**:
1. `push_subscriptions` 테이블에 토큰 저장
2. 이미 존재하면 업데이트
3. 한 사용자 여러 기기 등록 가능

---

## 8. 전체 API 명세 요약

| 기능 | Method | Endpoint | 설명 |
|------|--------|----------|------|
| 로그인/가입 | POST | /api/v1/users | 이메일 기반 사용자 식별 |
| 프로필 생성 | POST | /api/v1/profiles | 사주 정보 등록 및 간지 계산 |
| 프로필 목록 | GET | /api/v1/users/{user_id}/profiles | 사용자 프로필 목록 |
| 대표 설정 | PUT | /api/v1/profiles/{id}/primary | 대표 프로필 설정 |
| 프로필 삭제 | DELETE | /api/v1/profiles/{id} | 프로필 삭제 |
| 운세 조회 | GET | /api/v1/fortunes/today/{id} | 오늘 운세 조회 |
| 궁합 분석 | POST | /api/v1/compatibility | 두 사주 궁합 분석 |
| 토큰 등록 | POST | /api/v1/push/register | 푸시 토큰 저장 |

---

## 9. 서비스 시나리오 흐름 (Service Flow)
1. 사용자가 앱 접속 후 이메일 입력 → 사용자 생성 또는 로그인
2. 사주 정보 입력 → 프로필 생성 및 간지 계산 저장
3. 메인 화면 진입 → 오늘 운세 API 호출
4. DB에 오늘 운세 없으면 AI 운세 생성 후 저장
5. 지인 프로필 추가 후 궁합 분석 요청 → 실시간 AI 분석
6. 다음 날 아침 서버 스케줄러 실행
7. 대표 프로필 기준 오늘 운세 조회
8. 푸시 알림 발송