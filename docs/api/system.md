# 📑 System & Push API 상세 명세서
> **대상:** `push_subscriptions`, `system_metrics` 관리 및 모니터링

---

## 1. 푸시 알림 구독 등록 (Create Push Subscription)
- **Method:** `POST`
- **Endpoint:** `/api/v1/system/push/subscribe`
- **Description:** 사용자의 브라우저나 기기에서 생성된 고유 토큰을 저장하여 알림 발송 대상으로 등록합니다.

### [요청 형식 - Request Body]
```json
{
  "user_email": "user@example.com",
  "device_type": "WEB_CHROME",
  "subscription_token": "endpoint_url_or_fcm_token_string",
  "p256dh": "crypto_key_for_browser_push",
  "auth": "auth_secret_key"
}
```

### [응답 형식 - Response Body]
```json
{
  "status": 201,
  "data": { 
    "subscription_id": 88, 
    "is_active": true,
    "subscribed_at": "2026-04-07T21:00:00Z"
  }
}
```

### [에러 코드 - Error Codes]
- `400 Bad Request`: 구독 토큰(`subscription_token`)이 누락되었거나 지원하지 않는 기기 형식인 경우.
- `422 Unprocessable Entity`: 웹 푸시용 암호화 키(`p256dh`, `auth`)가 유효하지 않아 등록이 불가능한 경우.
- `500 Internal Server Error`: 구글(FCM) 등 외부 알림 서버와의 연동 실패 또는 DB 저장 오류.

---

## 2. 시스템 통계 조회 (Get System Metrics)
- **Method:** `GET`
- **Endpoint:** `/api/v1/admin/system/stats`
- **Description:** 관리자 페이지 대시보드에서 사용할 전체 지표(사용자 수, 성공률 등)를 한꺼번에 조회합니다.

### [요청 형식 - Request Body]
- **Headers:** `Authorization: Bearer {ADMIN_TOKEN}` (관리자 인증 토큰 필수)

### [응답 형식 - Response Body]
```json
{
  "status": 200,
  "data": {
    "total_users": 1250,
    "active_subscriptions": 980,
    "today_generated_fortunes": 342,
    "ai_success_rate": "98.5%",
    "server_uptime": "152h 30m"
  }
}
```

### [에러 코드 - Error Codes]
- `401 Unauthorized`: 관리자 인증 토큰이 없거나 만료된 경우.
- `403 Forbidden`: 일반 사용자가 관리자 전용 데이터에 접근하려고 할 때 발생.
- `500 Internal Server Error`: 대량의 데이터를 합산(Aggregation)하는 과정에서 서버 부하로 타임아웃이 발생한 경우.

---

## 3. 서버 헬스체크 (System Health Check)
- **Method:** `GET`
- **Endpoint:** `/api/v1/system/health`
- **Description:** 서버, 데이터베이스, AI 엔진이 모두 정상적으로 연결되어 작동 중인지 실시간으로 확인합니다.

### [요청 형식 - Request Body]
- 별도의 요청 파라미터 없음 (정기적인 자동 모니터링용)

### [응답 형식 - Response Body]
```json
{
  "status": 200,
  "data": {
    "api_server": "ALIVE",
    "database": "CONNECTED",
    "ai_engine": "READY",
    "last_check_at": "2026-04-07T21:05:00Z"
  }
}
```

### [에러 코드 - Error Codes]
- `503 Service Unavailable`: 서버는 켜져 있으나 DB가 죽어있는 등 서비스가 불가능한 심각한 상태일 때 발생.

---

## 4. 푸시 알림 구독 해제 (Delete Subscription)
- **Method:** `DELETE`
- **Endpoint:** `/api/v1/system/push/unsubscribe/{subscription_id}`
- **Description:** 더 이상 알림을 받지 않기로 한 기기의 정보를 시스템에서 완전히 삭제합니다.

### [요청 형식 - Request Body]
- **Path Variable:**
  - `subscription_id`: 삭제할 구독 정보의 고유 번호

### [응답 형식 - Response Body]
```json
{
  "status": 204,
  "message": "구독 정보가 성공적으로 제거되었습니다."
}
```

### [에러 코드 - Error Codes]
- `404 Not Found`: 삭제 요청한 구독 번호가 시스템에 존재하지 않는 경우.
- `500 Internal Server Error`: 데이터베이스에서 삭제 명령을 처리하던 중 오류 발생.

---

## 🛠 설계 핵심 포인트 (Business Logic)

1. **웹 푸시 보안 (`422` 에러):** 브라우저 푸시는 보안이 매우 중요합니다. 단순 주소뿐만 아니라 암호화 키(`p256dh`)가 정확해야만 알림이 가기 때문에, 이 값이 비어있거나 형식이 틀리면 등록을 거절하도록 설계했습니다.
2. **효율적인 지표 집계:** 관리자용 통계(`total_users` 등)는 매번 새로 계산하면 서버에 큰 무리를 줍니다. 실시간보다는 일정 시간(예: 1시간) 간격으로 미리 계산된 값을 보여주는 캐싱 방식을 권장합니다.
3. **위기 대응 시스템 (`503` 에러):** 서버가 켜져 있어도 DB 연결이 끊기면 운세를 보여줄 수 없습니다. 헬스체크 API는 이를 감지하여 문제가 생기면 즉시 관리자에게 알림(Slack 등)을 보내는 트리거 역할을 수행합니다.