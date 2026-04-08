# 📊 Inference Logs API 명세서
> **작성일:** 2026-04-08
> **대상:** `ai_inference_logs` 테이블 (AI 추론 과정 및 비용 모니터링 전용)

---

## 1. AI 추론 로그 목록 조회 (Get Inference Logs)
- **Method:** `GET`
- **Endpoint:** `/api/v1/admin/logs/ai`
- **Description:** 전체 AI 호출 이력을 목록 형태로 조회합니다. 모델명이나 성공 여부에 따라 필터링이 가능합니다.

### [요청 형식 - Request Body]
- **Query Params:**
  - `page`: 페이지 번호 (예: 1)
  - `size`: 한 번에 가져올 로그 개수 (예: 20)
  - `status`: 실행 결과 상태 (`SUCCESS` 또는 `FAIL`)
  - `model_name`: 사용된 모델명 (예: `gpt-4o`, `clova-x`)

### [응답 형식 - Response Body]
```json
{
  "status": 200,
  "data": {
    "items": [
      {
        "log_id": 5501,
        "profile_id": 45,
        "model_name": "gpt-4o",
        "total_tokens": 1270,
        "latency_ms": 3200,
        "status": "SUCCESS",
        "created_at": "2026-04-07T21:30:00Z"
      }
    ],
    "total": 12500
  }
}
```

### [에러 코드 - Error Codes]
- `401 Unauthorized`: 관리자 인증 정보가 없거나 유효하지 않음.
- `403 Forbidden`: 관리자 권한이 없어 접근이 거부됨.
- `500 Internal Server Error`: 서버에서 로그를 불러오는 중 타임아웃(시간 초과) 발생.

---

## 2. 특정 로그 상세 조회 (Get Log Detail)
- **Method:** `GET`
- **Endpoint:** `/api/v1/admin/logs/ai/{log_id}`
- **Description:** 특정 AI 호출에서 실제로 주고받은 프롬프트(질문)와 응답 원문을 확인합니다.

### [요청 형식 - Request Body]
- **Path Variable:**
  - `log_id`: 상세 내용을 볼 로그의 고유 식별 번호

### [응답 형식 - Response Body]
```json
{
  "status": 200,
  "data": {
    "log_id": 5501,
    "raw_prompt": "사용자 데이터: 을해년...",
    "raw_response": "{\"content\": \"행운이 가득합니다...\"}",
    "error_message": null
  }
}
```

### [에러 코드 - Error Codes]
- `404 Not Found`: 요청한 로그 번호(`log_id`)가 존재하지 않음.

---

## 3. 로그 데이터 정리 (Cleanup Logs)
- **Method:** `DELETE`
- **Endpoint:** `/api/v1/admin/logs/ai/cleanup`
- **Description:** 서버 용량 확보를 위해 특정 날짜 이전의 오래된 로그들을 한 번에 삭제합니다.

### [요청 형식 - Request Body]
- **Query Params:**
  - `before_date`: 삭제 기준일 (예: `2026-01-01` 입력 시 1월 1일 이전 데이터 삭제)

### [응답 형식 - Response Body]
```json
{
  "status": 200,
  "message": "3,450건의 로그가 성공적으로 정리되었습니다.",
  "data": { 
    "deleted_count": 3450 
  }
}
```

### [에러 코드 - Error Codes]
- `400 Bad Request`: 날짜 형식이 서버 규격과 맞지 않음.
- `401 Unauthorized`: 삭제 권한이 없는 사용자의 요청.

---

## 4. AI 모델별 비용 및 성능 통계 (Get Model Cost Stats)
- **Method:** `GET`
- **Endpoint:** `/api/v1/admin/logs/ai/stats`
- **Description:** 각 AI 모델이 얼마나 사용되었는지, 응답 속도는 어떤지, 예상 비용은 얼마인지 요약 리포트를 제공합니다.

### [요청 형식 - Request Body]
- **Query Params:**
  - `start_date`: 통계 집계를 시작할 날짜
  - `end_date`: 통계 집계를 마칠 날짜

### [응답 형식 - Response Body]
```json
{
  "status": 200,
  "data": [
    {
      "model_name": "gpt-4o",
      "total_calls": 1500,
      "success_rate": "99.2%",
      "avg_latency_ms": 2850,
      "usage": {
        "total_tokens": 1650000
      },
      "estimated_cost_usd": 12.45
    }
  ]
}
```

### [에러 코드 - Error Codes]
- `400 Bad Request`: 통계 기간(날짜 범위) 설정이 잘못됨.
- `500 Internal Server Error`: 대량의 데이터를 계산(집계 쿼리)하는 중 서버 오류 발생.

---

## 5. 특정 유저 추론 히스토리 조회 (Get User Inference History)
- **Method:** `GET`
- **Endpoint:** `/api/v1/admin/logs/ai/user/{profile_id}`
- **Description:** 특정 사용자가 지금까지 AI로부터 어떤 운세 응답을 받았는지 시간 순서대로 추적합니다.

### [요청 형식 - Request Body]
- **Path Variable:**
  - `profile_id`: 추적하려는 프로필의 고유 번호

### [응답 형식 - Response Body]
```json
{
  "status": 200,
  "data": {
    "profile_id": 45,
    "history": [
      {
        "log_id": 9821,
        "model_name": "gpt-4o",
        "raw_prompt": "사용자 사주 데이터...",
        "raw_response": "{\"content\": \"...\"}",
        "created_at": "2026-04-07T09:15:22Z"
      }
    ]
  }
}
```

### [에러 코드 - Error Codes]
- `404 Not Found`: 해당 프로필 번호에 대한 AI 상담 기록이 전혀 없음.