# 📑 User & Profile API 상세 명세서
> **작성일:** 2026-04-07  
> **대상:** `users`, `saju_profiles` 테이블 통합 관리

---

## 1. 회원 생성 (Create User)
- **Method:** `POST`
- **Endpoint:** `/api/v1/admin/users`
- **Description:** 시스템에 새로운 사용자를 수동으로 등록합니다.

### [요청 형식 - Request Body]
```json
{
  "email": "new_user@example.com"
}
```

### [응답 형식 - Response Body]
```json
{
  "status": 201,
  "data": { 
    "email": "new_user@example.com", 
    "created_at": "2026-04-07T20:00:00Z" 
  }
}
```

### [에러 코드 - Error Codes]
- `400 Bad Request`: 이미 존재하는 이메일이거나 이메일 형식이 누락된 경우.
- `401 Unauthorized`: 관리자 인증 토큰(Bearer Token)이 유효하지 않음.
- `403 Forbidden`: 관리자 권한이 없는 계정으로 접근 시 발생.

---

## 2. 회원 목록 조회 (Get Users)
- **Method:** `GET`
- **Endpoint:** `/api/v1/admin/users`
- **Description:** 전체 회원 목록을 페이징하여 조회합니다.

### [요청 형식 - Query Params]
- `page`: 페이지 번호 (예: 1)
- `size`: 한 페이지당 불러올 회원 수 (예: 20)
- `keyword`: 검색하고자 하는 이메일 키워드

### [응답 형식 - Response Body]
```json
{
  "status": 200,
  "data": {
    "items": [
      { "email": "user1@test.com", "created_at": "2026-04-01T10:00:00Z" }
    ],
    "total": 150
  }
}
```

### [에러 코드 - Error Codes]
- `401 Unauthorized`: 관리자 권한 없음.
- `500 Internal Server Error`: 데이터베이스 목록 조회 중 서버 오류 발생.

---

## 3. 회원 정보 업데이트 (Update User)
- **Method:** `PATCH`
- **Endpoint:** `/api/v1/admin/users/{email}`
- **Description:** 사용자의 상태(로그인 시간 등)를 강제로 수정합니다.

### [요청 형식 - Request Body]
```json
{
  "last_login": "2026-04-07T20:30:00Z"
}
```

### [응답 형식 - Response Body]
```json
{ "status": 200, "message": "회원 정보가 수정되었습니다." }
```

### [에러 코드 - Error Codes]
- `404 Not Found`: 수정하려는 이메일의 회원이 존재하지 않음.
- `422 Unprocessable Entity`: 날짜 데이터 형식이 잘못됨 (예: 숫자가 아닌 문자열 등).

---

## 4. 회원 삭제 (Delete User)
- **Method:** `DELETE`
- **Endpoint:** `/api/v1/admin/users/{email}`
- **Description:** 회원을 삭제합니다. 연관된 모든 사주 프로필 데이터가 함께 제거됩니다.

### [응답 형식 - Response Body]
```json
{ "status": 204, "message": "회원이 성공적으로 삭제되었습니다." }
```

### [에러 코드 - Error Codes]
- `404 Not Found`: 삭제하려는 회원을 찾을 수 없음.

---

## 5. 사주 프로필 생성 (Create Saju Profile)
- **Method:** `POST`
- **Endpoint:** `/api/v1/admin/profiles`
- **Description:** 특정 유저에게 귀속되는 사주 프로필을 생성합니다.

### [요청 형식 - Request Body]
```json
{
  "user_email": "user1@test.com",
  "nickname": "본체",
  "birth_date": "1995-12-25",
  "birth_time": "08:30",
  "gender": "FEMALE"
}
```

### [응답 형식 - Response Body]
```json
{
  "status": 201,
  "data": { "profile_id": 45, "nickname": "본체" }
}
```

### [에러 코드 - Error Codes]
- `400 Bad Request`: 필수 지표(생년월일, 성별 등) 누락.
- `422 Unprocessable Entity`: 성별 값이 `MALE`, `FEMALE`이 아닌 경우 또는 생시 형식이 잘못된 경우.

---

## 6. 사주 프로필 조회 (Get Profile)
- **Method:** `GET`
- **Endpoint:** `/api/v1/admin/profiles/{profile_id}`
- **Description:** 특정 사주 프로필의 상세 정보 및 간지(Ganji) 데이터를 조회합니다.

### [응답 형식 - Response Body]
```json
{
  "status": 200,
  "data": {
    "profile_id": 45,
    "year_ganji": "을해(乙亥)",
    "month_ganji": "기축(己丑)",
    "day_ganji": "정묘(丁卯)"
  }
}
```

### [에러 코드 - Error Codes]
- `404 Not Found`: 해당 `profile_id`를 가진 프로필이 없음.

---

## 7. 사주 프로필 수정 (Update Profile)
- **Method:** `PATCH`
- **Endpoint:** `/api/v1/admin/profiles/{profile_id}`
- **Description:** 프로필의 닉네임이나 생시 등을 수정합니다.

### [요청 형식 - Request Body]
```json
{
  "nickname": "닉네임변경",
  "birth_time": "12:00"
}
```

### [응답 형식 - Response Body]
```json
{ "status": 200, "message": "프로필 수정 완료" }
```

---

## 8. 사주 프로필 삭제 (Delete Profile)
- **Method:** `DELETE`
- **Endpoint:** `/api/v1/admin/profiles/{profile_id}`
- **Description:** 특정 사주 프로필을 개별적으로 삭제합니다.

---

## 9. 대표 프로필 설정 (Set Primary Profile)
- **Method:** `PATCH`
- **Endpoint:** `/api/v1/admin/profiles/{profile_id}/primary`
- **Description:** 해당 프로필을 유저의 기본(대표) 프로필로 설정합니다.

### [응답 형식 - Response Body]
```json
{
  "status": 200,
  "data": { "profile_id": 45, "is_primary": true }
}
```

---

## 🛠 설계 핵심 포인트 (Business Logic)

1. **데이터 정합성 (`400`, `422`):** 성별이나 날짜 형식을 서버에서 엄격히 체크하여 잘못된 데이터가 DB에 쌓이는 것을 방지합니다.
2. **연쇄 삭제 (Cascade):** 회원을 삭제하면 관련 프로필이 모두 삭제되므로 관리 시 주의가 필요함을 에러 메시지나 문서에 명시합니다.
3. **비즈니스 가치:** 조회 시 간지(Ganji) 데이터를 포함하여, 사주 서비스의 핵심 로직인 '만세력 계산' 결과값을 프론트엔드에 즉시 제공합니다.