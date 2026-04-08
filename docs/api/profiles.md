# 🔮 Profiles API 명세서
> **작성일:** 2026-04-08
> **대상:** `saju_profiles` 테이블 관리 (식별자: `profile_id`)

---

## 1. 사주 프로필 생성 (Create Profile)
- **Method:** `POST`
- **Endpoint:** `/api/v1/profiles`
- **Description:** 새로운 사주 프로필을 생성합니다. (한 사람당 최대 5개까지 생성 가능)

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
  "data": { 
    "profile_id": 45, 
    "nickname": "본체" 
  }
}
```

### [에러 코드 - Error Codes]
- `400 Bad Request`: 필수 값(생년월일 등)이 누락되었거나, 이미 5개의 프로필을 보유한 경우.
- `422 Unprocessable Entity`: 성별 값이 규격(`MALE`, `FEMALE`)에 맞지 않거나 시간 형식이 틀린 경우.

---

## 2. 유저별 프로필 목록 조회 (Get My Profiles)
- **Method:** `GET`
- **Endpoint:** `/api/v1/profiles`
- **Description:** 특정 유저가 만든 모든 프로필 리스트를 간단하게 보여줍니다.

### [요청 형식 - Request Body]
- **Query Params:**
  - `user_email`: 조회를 원하는 유저의 이메일 (필수)

### [응답 형식 - Response Body]
```json
{
  "status": 200,
  "data": {
    "user_email": "user@example.com",
    "profiles": [
      { "profile_id": 45, "nickname": "본체", "is_primary": true },
      { "profile_id": 126, "nickname": "친구1", "is_primary": false }
    ]
  }
}
```

### [에러 코드 - Error Codes]
- `400 Bad Request`: 필수 파라미터인 `user_email`이 전달되지 않음.

---

## 3. 사주 프로필 상세 조회 (Get Profile Detail)
- **Method:** `GET`
- **Endpoint:** `/api/v1/profiles/{profile_id}`
- **Description:** 특정 프로필의 상세 정보와 계산된 만세력(사주 팔자 간지) 데이터를 조회합니다.

### [요청 형식 - Request Body]
- **Path Variable:**
  - `profile_id`: 조회하고 싶은 프로필의 고유 번호

### [응답 형식 - Response Body]
```json
{
  "status": 200,
  "data": {
    "profile_id": 45,
    "nickname": "본체",
    "year_ganji": "을해(乙亥)",
    "month_ganji": "기축(己丑)",
    "day_ganji": "정묘(丁卯)",
    "is_primary": true
  }
}
```

### [에러 코드 - Error Codes]
- `404 Not Found`: 해당 번호(`profile_id`)를 가진 프로필이 시스템에 없음.

---

## 4. 사주 프로필 수정 (Update Profile)
- **Method:** `PATCH`
- **Endpoint:** `/api/v1/profiles/{profile_id}`
- **Description:** 프로필 정보를 수정합니다. 바꾸고 싶은 필드만 골라서 보낼 수 있습니다.

### [요청 형식 - Request Body]
```json
{
  "nickname": "새로운 닉네임",
  "birth_time": "14:30"
}
```

### [응답 형식 - Response Body]
```json
{
  "status": 200,
  "message": "성공적으로 수정되었습니다.",
  "data": {
    "profile_id": 45,
    "updated_fields": ["nickname", "birth_time"]
  }
}
```

### [에러 코드 - Error Codes]
- `400 Bad Request`: 날짜나 시간 형식이 서버에서 정한 규칙과 다름.
- `404 Not Found`: 수정하려는 프로필 번호가 존재하지 않음.

---

## 5. 대표 프로필 설정 (Set Primary Profile)
- **Method:** `PATCH`
- **Endpoint:** `/api/v1/profiles/{profile_id}/primary`
- **Description:** 선택한 프로필을 '메인(대표)'으로 설정합니다. 기존에 메인이었던 프로필은 자동으로 일반 프로필로 변경됩니다.

### [요청 형식 - Request Body]
- **Path Variable:**
  - `profile_id`: 대표로 만들고 싶은 프로필의 고유 번호

### [응답 형식 - Response Body]
```json
{
  "status": 200,
  "message": "성공적으로 대표 프로필이 변경되었습니다.",
  "data": {
    "user_email": "user@example.com",
    "primary_profile_id": 45,
    "is_primary": true
  }
}
```

### [에러 코드 - Error Codes]
- `401 Unauthorized`: 내 프로필이 아니어서 변경 권한이 없거나 로그인이 안 됨.
- `500 Internal Server Error`: 메인 프로필을 교체하는 과정에서 서버 데이터베이스 오류 발생.

---

## 6. 사주 프로필 삭제 (Delete Profile)
- **Method:** `DELETE`
- **Endpoint:** `/api/v1/profiles/{profile_id}`
- **Description:** 특정 프로필을 영구히 삭제합니다.

### [요청 형식 - Request Body]
- **Path Variable:**
  - `profile_id`: 삭제할 프로필의 고유 번호
- **Query Params:**
  - `reason`: 삭제 사유 (선택 사항)

### [응답 형식 - Response Body]
```json
{
  "status": 204,
  "message": "프로필 삭제가 완료되었습니다."
}
```

### [에러 코드 - Error Codes]
- `401 Unauthorized`: 본인이 만든 프로필이 아니면 지울 수 없음.
- `404 Not Found`: 삭제 요청한 번호의 프로필을 찾을 수 없음.