# DailyFortune + FortunePhrase (운세 데이터)
# 📑 Daily Fortune API 상세 명세서
> **작성일:** 2026-04-07  
> **대상:** `daily_fortunes`, `fortune_phrases` 테이블 및 추론 상태 관리

---

## 1. 오늘의 운세 생성 (Create Daily Fortune)
- **Method:** `POST`
- **Endpoint:** `/api/v1/admin/fortunes`
- **Description:** 특정 프로필의 사주 데이터를 기반으로 생성된 운세 결과와 그래프용 수치 데이터를 저장합니다.
- **Request Body (JSON):**
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
- **Error Codes:**
  - `400 Bad Request`: 필수 지표(score 등) 누락 또는 숫자가 아닌 형식 입력 시 발생.
  - `422 Unprocessable Entity`: 입력된 점수가 비정상적(예: 음수 또는 100점 초과)인 경우.
  - `429 Too Many Requests`: AI 진단 API 호출 할당 초과 (단시간 반복 진단 방지).
  - `500 Internal Server Error`: AI 엔진 연산 오류 또는 JSONB 스냅샷 저장 실패.

---

## 2. 오늘의 운세 일괄 조회 (Get Today's Fortune)
- **Method:** `GET`
- **Endpoint:** `/api/v1/admin/fortunes/{profile_id}/today`
- **Description:** 방사형 그래프용 5가지 점수 세트와 운세 총평을 한 번에 조회합니다.
- **Response Body (JSON):**
```json
{
  "status": 200,
  "data": {
    "content": "오늘은 북쪽에서 귀인을 만날 운세입니다.",
    "radar_chart": { "money": 95, "love": 70, "health": 80, "work": 90, "total": 88 },
    "status": "SUCCESS"
  }
}
```
- **Error Codes:**
  - `400 Bad Request`: 유효하지 않은 `profile_id` 형식.
  - `404 Not Found`: 해당 프로필의 오늘 운세 데이터가 존재하지 않음.
  - `500 Internal Server Error`: DB 조회 중 예기치 못한 오류 발생.

---

## 3. 운세 생성 실패 기록 (Post Fortune Failure)
- **Method:** `POST`
- **Endpoint:** `/api/v1/admin/fortunes/fail`
- **Description:** AI 서버 장애나 데이터 오류로 운세 생성에 실패했을 때 원인을 기록합니다.
- **Request Body (JSON):**
```json
{
  "profile_id": 45,
  "status": "FAIL",
  "error_msg": "AI_SERVER_TIMEOUT"
}
```
- **Error Codes:**
  - `400 Bad Request`: 필수 필드(`status`, `error_msg`) 누락.
  - `500 Internal Server Error`: 로그 데이터 저장 실패.

---

## 4. 랜덤 운세 문구 등록 (Create Fortune Phrase)
- **Method:** `POST`
- **Endpoint:** `/api/v1/admin/fortune-phrases`
- **Description:** 화면 하단에 노출할 짧은 덕담 데이터를 등록합니다.
- **Request Body (JSON):**
```json
{
  "category": "LUCK",
  "phrase": "작은 친절이 큰 행운으로 돌아오는 하루입니다."
}
```
- **Error Codes:**
  - `400 Bad Request`: 문구 내용이 비어있거나 형식이 잘못된 경우.
  - `422 Unprocessable Entity`: 허용되지 않은 카테고리 입력.

---

## 5. 랜덤 운세 문구 조회 (Get Random Phrase)
- **Method:** `GET`
- **Endpoint:** `/api/v1/admin/fortune-phrases/random`
- **Description:** 등록된 문구 중 하나를 무작위로 호출합니다.
- **Error Codes:**
  - `404 Not Found`: 등록된 운세 문구가 하나도 없는 경우.
  - `500 Internal Server Error`: 무작위 추출 연산 중 서버 오류.

---

## 🛠 설계 포인트 요약

* **데이터 무결성(`400`, `422`):** 점수 데이터가 음수로 들어오거나 형식이 깨지는 것을 방지하여 프론트엔드 그래프 깨짐 현상을 차단합니다.
* **비용 관리(`429`):** 무분별한 AI 호출을 막아 API 비용 폭증을 방지합니다.
* **장애 추적(`500`):** AI 엔진 연산이나 DB 스냅샷 저장 실패 시 관리자가 즉시 원인을 파악할 수 있도록 표준화된 에러를 반환합니다.