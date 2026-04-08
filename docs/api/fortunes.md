# 📑 Daily Fortune API 상세 명세서

> **대상:** `daily_fortunes`, `fortune_phrases` 테이블 및 추론 상태 관리

---

## 1. 오늘의 운세 생성 (Create Daily Fortune)
- **Method:** `POST`
- **Endpoint:** `/api/v1/fortunes`
- **Description:** 특정 유저 사주 데이터를 기반으로 생성된 운세 결과와 그래프용 수치 데이터를 저장합니다.

### [요청 형식 - Request Body]
```json
{
  "profile_id": 45,
  "content": "오늘은 북쪽에서 귀인을 만날 운세입니다.",
  "fortune_score": 88,
  "money_score": 95,
  "love_score": 70,
  "health_score": 80,
  "work_score": 90,
  "status": "SUCCESS"
}
```

### [응답 형식 - Response Body]
```json
{
  "status": 201,
  "message": "운세 데이터가 성공적으로 생성되었습니다.",
  "data": {
    "fortune_id": 1205,
    "profile_id": 45,
    "created_at": "2026-04-08T10:00:00Z"
  }
}
```

### [에러 코드 - Error Codes]
- `400 Bad Request`: 필수 지표(점수 등)가 누락되었거나 숫자가 아닌 형식이 입력된 경우.
- `422 Unprocessable Entity`: 입력된 점수가 비정상적(음수 또는 100점 초과)이라 처리가 불가능한 경우.
- `429 Too Many Requests`: 짧은 시간 내 반복 호출로 AI API 할당량을 초과한 경우.
- `500 Internal Server Error`: AI 엔진 연산 중 오류가 발생했거나 데이터베이스 저장에 실패한 경우.

---

## 2. 오늘의 운세 조회 (Get Today's Fortune)
- **Method:** `GET`
- **Endpoint:** `/api/v1/fortunes/{profile_id}/today`
- **Description:** 방사형 그래프(Radar Chart)에 사용될 5가지 점수와 운세 총평을 한 번에 가져옵니다.

### [요청 형식 - Request Body]
- **Path Variable:**
  - `profile_id`: 조회하고 싶은 유저의 프로필 고유 번호

### [응답 형식 - Response Body]
```json
{
  "status": 200,
  "data": {
    "content": "오늘은 북쪽에서 귀인을 만날 운세입니다.",
    "radar_chart": { 
      "money": 95, 
      "love": 70, 
      "health": 80, 
      "work": 90, 
      "total": 88 
    },
    "status": "SUCCESS"
  }
}
```

### [에러 코드 - Error Codes]
- `400 Bad Request`: 잘못된 형식의 `profile_id`가 전달된 경우.
- `404 Not Found`: 해당 프로필에 대해 오늘 생성된 운세 데이터가 아직 없는 경우.
- `500 Internal Server Error`: 데이터베이스 조회 중 예상치 못한 기술적 오류 발생.

---

## 🛠 설계 핵심 포인트 (Core Points)

1. **데이터 무결성(`400`, `422`):** 프론트엔드에서 방사형 그래프를 그릴 때 점수가 0~100 범위를 벗어나면 화면이 깨질 수 있습니다. 따라서 백엔드 저장 단계에서 엄격한 검증(Validation)이 필수입니다.
2. **비용 효율성(`429`):** AI 추론(LLM 호출)은 건당 비용이 발생합니다. 동일 사용자가 하루에 수십 번 호출하여 비용이 낭비되지 않도록 '하루 1회 생성' 또는 '캐싱' 로직을 적용해야 합니다.
3. **확장성:** 현재는 `today` 고정 엔드포인트지만, 나중에는 과거 운세를 볼 수 있도록 날짜 파라미터(`?date=2026-04-07`)를 추가하여 확장하기 좋은 구조로 설계되었습니다.