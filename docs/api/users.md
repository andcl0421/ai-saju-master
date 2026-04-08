# 📑 User & Profile API 상세 명세서
> **작성일:** 2026-04-08
> **대상:** `users`, `saju_profiles` 테이블 통합 관리

---

## 1. 회원 생성 (Create User)
- **Method:** `POST`
- **Endpoint:** `/api/v1/users`
- **Description:** 시스템에 새로운 사용자를 등록합니다.

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

---

## 2. 회원 목록 조회 (Get Users - Admin)
- **Method:** `GET`
- **Endpoint:** `/api/v1/users`
- **Description:** 전체 회원 목록을 페이징하여 조회합니다. (관리자 권한 필요)

### [요청 형식 - Request Body]
- **Query Params:**
  - `page`: 페이지 번호 (기본값: 1)
  - `size`: 한 페이지당 불러올 회원 수 (기본값: 20)
  - `keyword`: 검색하고자 하는 이메일 키워드 (Optional)

### [응답 형식 - Response Body]
```json
{
  "status": 200,
  "data": {
    "items": [
      { 
        "email": "user1@test.com", 
        "created_at": "2026-04-01T10:00:00Z" 
      }
    ],
    "total": 150
  }
}
```

### [에러 코드 - Error Codes]
- `401 Unauthorized`: 관리자 권한 없음.
- `500 Internal Server Error`: 데이터베이스 목록 조회 중 서버 오류 발생.

---

## 3. 회원 상세 조회 (Get User Detail)
- **Method:** `GET`
- **Endpoint:** `/api/v1/users/{email}`
- **Description:** 특정 회원의 가입일, 최근 접속일, 프로필 개수 등 상세 데이터를 조회합니다.

### [요청 형식 - Request Body]
- **Path Variable:**
  - `email`: 조회 대상 사용자의 이메일 주소

### [응답 형식 - Response Body]
```json
{
  "status": 200,
  "data": {
    "email": "user@example.com",
    "created_at": "2026-04-01T10:00:00Z",
    "last_login_at": "2026-04-07T20:30:00Z",
    "is_active": true,
    "profile_count": 3,
    "primary_profile_id": 45
  }
}
```

### [에러 코드 - Error Codes]
- `401 Unauthorized`: 관리자 인증 토큰이 유효하지 않음.
- `404 Not Found`: 해당 이메일을 가진 회원이 존재하지 않음.

---

## 4. 회원 삭제 (Delete User - Admin)
- **Method:** `DELETE`
- **Endpoint:** `/api/v1/users/{email}`
- **Description:** 회원을 영구 삭제합니다. 사주 프로필 등 연관 데이터가 연쇄 삭제(Cascade Delete)됩니다.

### [요청 형식 - Request Body]
- **Path Variable:**
  - `email`: 삭제 대상 사용자의 이메일 주소
- **Query Params:**
  - `reason`: 삭제 사유 (Optional)

### [응답 형식 - Response Body]
```json
{
  "status": 204,
  "message": "사용자 정보 및 연관 데이터가 성공적으로 삭제되었습니다."
}
```

### [에러 코드 - Error Codes]
- `401 Unauthorized`: 관리자 권한 없음.
- `404 Not Found`: 삭제하려는 이메일을 가진 회원이 존재하지 않음.