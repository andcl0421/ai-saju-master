# FortuneLog (AI 추론 감시)

# 📑 AI Fortune Log API 상세 명세서
> **작성일:** 2026-04-07  
> **대상:** `ai_inference_logs` 테이블 (추론 과정 및 비용 모니터링)

---

## 1. AI 추론 로그 기록 (Create Inference Log)
- **Method:** `POST`
- **Endpoint:** `/api/v1/admin/logs/ai`
- **Description:** AI 모델 호출 시 사용된 프롬프트, 모델명, 토큰 사용량 및 실행 시간을 기록하여 시스템의 투명성을 확보합니다.

### [요청 형식 - Request Body]
```json
{
  "profile_id": 45,
  "model_name": "gpt-4o",
  "prompt_tokens": 850,
  "completion_tokens": 420,
  "total_tokens": 1270,
  "latency_ms": 3200,
  "status": "SUCCESS",
  "raw_prompt": "사용자 사주 데이터: ... 이 데이터를 기반으로 오늘의 운세를 생성해줘.",
  "raw_response": "{\"content\": \"오늘은 재물운이...\", \"scores\": {...}}"
}
```

### [응답 형식 - Response Body]
```json
{
  "status": 201,
  "message": "추론 로그가 성공적으로 기록되었습니다."
}
```

### [에러 코드 - Error Codes]
- `400 Bad Request`: 필수 지표(tokens, status 등) 누락 혹은 데이터 형식 오류.
- `422 Unprocessable Entity`: 토큰 사용량이 음수이거나 논리적으로 불가능한 수치인 경우.
- `500 Internal Server Error`: 로그 저장용 DB 연결 오류 또는 JSON 데이터 처리 실패.

---

## 2. AI 추론 로그 목록 조회 (Get Inference Logs)
- **Method:** `GET`
- **Endpoint:** `/api/v1/admin/logs/ai`
- **Description:** 전체 AI 호출 이력을 페이징하여 조회합니다. 특정 모델이나 성공/실패 여부로 필터링이 가능합니다.

### [요청 형식 - Query Params]
- `page=1`, `size=20`
- `status`: "SUCCESS" 또는 "FAIL"
- `model_name`: "gpt-4o", "clova-x" 등

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
- `401 Unauthorized`: 관리자 인증 토큰 누락.
- `500 Internal Server Error`: 대량 로그 데이터 집계 중 서버 타임아웃 발생.

---

## 3. 특정 로그 상세 조회 (Get Log Detail)
- **Method:** `GET`
- **Endpoint:** `/api/v1/admin/logs/ai/{log_id}`
- **Description:** 특정 AI 호출에서 실제 어떤 질문(Prompt)을 던졌고 어떤 답변(Response)을 받았는지 원문을 확인합니다.

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
- `404 Not Found`: 존재하지 않는 로그 ID.

---

## 4. 로그 데이터 정리 (Cleanup Logs)
- **Method:** `DELETE`
- **Endpoint:** `/api/v1/admin/logs/ai/cleanup`
- **Description:** DB 용량 관리를 위해 특정 날짜 이전의 오래된 로그를 일괄 삭제합니다.

### [요청 형식 - Query Params]
- `before_date`: "2026-01-01" (해당 날짜 이전 데이터 삭제)

### [응답 형식 - Response Body]
```json
{
  "status": 200,
  "message": "3,450건의 로그가 성공적으로 정리되었습니다."
}
```

---

## 🛠 설계 핵심 포인트 (Admin Insights)

1. **비용 모니터링 (`tokens`):** 프롬프트 토큰과 결과 토큰을 나누어 기록함으로써, 어떤 단계에서 비용이 많이 발생하는지 추적할 수 있습니다.
2. **성능 모니터링 (`latency_ms`):** AI 응답 속도가 느려지면 사용자 경험이 저하됩니다. 이 지표를 통해 모델 최적화나 서버 교체 시점을 판단합니다.
3. **디버깅 (`raw_data`):** AI가 잘못된 운세 결과를 내놓았을 때, 실제 API에 전달된 프롬프트를 확인하여 '프롬프트 엔지니어링'을 수정하는 근거로 활용합니다.