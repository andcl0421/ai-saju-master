# PushSubscription + 시스템 통계

<!-- 추후예정 -->

# 📑 System & Push API 상세 명세서
> **작성일:** 2026-04-07  
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
- `400 Bad Request`: 구독 토큰(`subscription_token`) 누락 또는 잘못된 기기 형식.
- `422 Unprocessable Entity`: 암호화 키(`p256dh`, `auth`)의 유효성 검증 실패.
- `500 Internal Server Error`: 푸시 서버(FCM 등) 연동 실패 또는 DB 저장 오류.

---

## 2. 시스템 통계 조회 (Get System Metrics)
- **Method:** `GET`
- **Endpoint:** `/api/v1/admin/system/stats`
- **Description:** 관리자 페이지 대시보드용 전체 데이터 통계를 일괄 조회합니다.

### [요청 형식 - Request]
- **Headers:** `Authorization: Bearer {ADMIN_TOKEN}`

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
- `401 Unauthorized`: 유효하지 않은 관리자 토큰.
- `403 Forbidden`: 시스템 통계 접근 권한 없음.
- `500 Internal Server Error`: 대규모 데이터 집계(Aggregation) 중 타임아웃 발생.

---

## 3. 서버 헬스체크 (System Health Check)
- **Method:** `GET`
- **Endpoint:** `/api/v1/system/health`
- **Description:** 서버와 DB, AI 엔진의 연결 상태를 실시간으로 확인합니다. (모니터링 도구용)

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
- `503 Service Unavailable`: DB 연결 끊김 등 핵심 서비스 이용 불가 시 발생.

---

## 4. 푸시 알림 구독 해제 (Delete Subscription)
- **Method:** `DELETE`
- **Endpoint:** `/api/v1/system/push/unsubscribe/{subscription_id}`
- **Description:** 더 이상 알림을 받지 않는 기기의 토큰 정보를 삭제합니다.

### [에러 코드 - Error Codes]
- `404 Not Found`: 존재하지 않는 구독 ID.
- `500 Internal Server Error`: 삭제 처리 중 데이터베이스 오류.

---

## 🛠 설계 핵심 포인트 (Business Logic)

1. **푸시 구독의 특성 (`422` 에러 관련):** 브라우저 푸시(Web Push)는 단순 토큰 외에도 보안을 위한 암호화 키(`p256dh`)가 필수입니다. 이 데이터가 깨져서 들어오면 알림을 보낼 수 없으므로 `422` 코드로 엄격하게 검증합니다.
2. **시스템 통계의 효율성:** `total_users` 같은 데이터는 사용자가 접속할 때마다 계산하면 서버가 힘들어합니다. 따라서 이 엔드포인트는 관리자가 대시보드를 열 때만 호출하거나, 1시간 단위로 캐싱된 데이터를 보여주는 방식을 권장합니다.
3. **헬스체크(`503` 에러)의 목적:** 서버가 살아있더라도 DB가 죽어있으면 서비스는 불가능합니다. 각 지표를 개별적으로 체크하여 문제가 생기면 즉시 `503` 코드를 뱉어 관리자에게 경고(Slack 알림 등)를 보내기 위함입니다.