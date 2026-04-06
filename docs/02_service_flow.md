# 📂 02_service_flow.md
## 서비스 동작 흐름 (Service Flow)

---

## 1. 전체 서비스 흐름

본 서비스는 사용자의 사주 프로필을 생성하고,
해당 프로필을 기반으로 매일 운세 데이터를 생성 및 저장한 뒤 사용자에게 제공하는 구조로 동작한다.

동일한 날짜에는 동일한 운세 결과를 제공하여 데이터 일관성과 서비스 신뢰성을 유지한다.

전체 흐름은 다음과 같다.

1. 사용자 접속 → 이메일 입력 → 사용자 생성 또는 조회
2. 사용자 프로필 생성
3. 사주 원국(간지) 계산
4. 오늘 운세 조회 요청
5. 기존 운세 데이터 조회
6. 없으면 운세 생성
7. 운세 결과 저장
8. 사용자에게 결과 반환
9. 푸시 알림 발송

---

## 2. 사용자 접속 Flow

### Step 1. 사용자 최초 접속
- 사용자가 웹 또는 앱에 최초 접속한다.
- 사용자는 이메일을 입력한다.
- 서버는 users 테이블에서 이메일 존재 여부를 확인한다.

### Step 2. 사용자 생성 또는 조회
- 이메일이 존재하면 기존 user_id 조회
- 이메일이 없으면 users 테이블에 신규 사용자 생성
- created_at 저장
- 이후 접속 시 last_login 업데이트

Flow:

User → Email 입력 → users 조회
      → 존재 → 로그인
      → 없음 → users 생성 → 로그인

---

## 3. 프로필 생성 Flow

사용자는 자신의 사주 분석을 위해 프로필 정보를 입력한다.

### 입력 정보
- nickname (닉네임)
- birth_date (생년월일)
- calendar_type (양력/음력)
- birth_time (태어난 시간)
- gender (성별)

### 서버 처리 과정
1. 사용자 입력 데이터 저장
2. calendar_type (SOLAR / LUNAR) 확인
3. 만세력 라이브러리에서 달력 유형에 맞게 간지 계산
4. 년주, 월주, 일주, 시주 생성
5. 계산된 간지 데이터를 saju_profiles 테이블에 저장

Flow:

User Input → calendar_type 확인 → 만세력 계산 → 간지 생성 → saju_profiles 저장

---

## 4. 사주 계산 Flow

사주 계산은 프로필 생성 시 1회 수행되며,
이후 운세 생성 시 재사용하기 위해 간지 데이터를 DB에 저장하여 캐싱한다.

### 사주 계산 과정
1. 사용자 생년월일, 태어난 시간,성별, calendar_type 입력
2. 만세력 라이브러리를 이용하여 calendar_type에 맞게 간지 계산
3. 년주, 월주, 일주, 시주 생성
4. 계산된 간지 데이터를 saju_profiles 테이블에 저장

저장 데이터:
- year_ganji
- month_ganji
- day_ganji
- time_ganji

---

## 5. 오늘의 운세 조회 Flow

사용자가 오늘 운세 조회 버튼 또는 메인 화면 접속 시 실행된다.

### 처리 과정

1. profile_id 확인
2. 오늘 날짜(target_date) 확인
3. daily_fortunes 테이블 조회

조건:
- profile_id
- target_date

### 분기 처리

#### Case 1. 오늘 운세 데이터 존재
→ DB에 저장된 운세 결과 반환

#### Case 2. 오늘 운세 데이터 없음
→ 운세 생성 Flow 실행

Flow:

Request → daily_fortunes 조회 → 
존재 → Return  
없음 → 운세 생성

---

## 6. 운세 생성 Flow (Hybrid AI)

운세 생성은 DB 문장 + AI 생성 문장을 결합하는 Hybrid 방식으로 수행된다.

### 운세 생성 과정

1. 오늘 날짜 간지 계산
2. 사용자 사주 간지 데이터 조회
3. Phrase 조회
4.Vector DB 검색 (RAG)
5. LLM 프롬프트 생성
6. LLM 호출
7. Function Calling 필요 여부 판단
8. Tool 호출 (간지 / 외부 데이터)
9. Tool 결과 반환
10. LLM 최종 운세 생성
11. 점수 생성
12. DB 저장

Flow:

Ganji 계산 → Phrase 조회 → RAG 검색 → LLM → 결과 생성 → DB 저장

---

## 7. 데이터 저장 Flow

운세 생성 후 다음 데이터가 저장된다.

### daily_fortunes 저장 데이터
- profile_id
- target_date
- fortune_score
- money_score
- love_score
- health_score
- work_score
- content (최종 운세 문장)
- luck_item
- created_at

### fortune_logs 저장 데이터
- profile_id
- prompt
- response
- target_date
- created_at

이를 통해 AI 응답 분석 및 모델 개선이 가능하다.

---

## 8. 푸시 알림 Flow [추후 구현 예정]

푸시 알림은 서비스 활성화를 위한 고도화 단계에서 도입하며, 대표 프로필(is_primary = true)을 기준으로 발송됩니다.

### 푸시 알림 과정

1. **스케줄러 작동:** 매일 정해진 아침 시간(예: AM 07:00)에 `APScheduler` 실행
2. **대상 필터링:** 대표 프로필(`is_primary = true`) 및 푸시 동의 유저 조회
3. **메시지 생성:** 오늘 운세 요약본 구성
4. **FCM 발송:** `push_subscriptions`의 토큰을 사용하여 기기로 알림 전송

Flow:

Scheduler → 대표 프로필 조회 → 오늘 운세 조회 → Push 전송

---

## 9. 전체 서비스 시퀀스

전체 서비스 흐름 요약:

1. 사용자 접속 → 이메일 입력 → 사용자 생성 또는 조회
2. 프로필 생성 → 사주 계산 → DB 저장
3. 오늘 운세 조회 요청
4. daily_fortunes 조회
5. 없으면 운세 생성
6. Hybrid AI 생성 (DB + LLM + RAG)
7. 운세 저장
8. 로그 저장
9. 사용자에게 결과 반환
10. 다음 날 푸시 알림 발송

---

## 10. AI 인연 궁합 Flow (Compatibility)

사용자가 등록된 두 개의 프로필을 선택하여 상호 간의 궁합을 분석하는 흐름이다. 
별도의 결과 저장을 하지 않는 휘발성 조회 방식을 채택한다.

1. **사용자가 궁합 보기 클릭**
2. **프로필 A 선택** (나)
3. **프로필 B 선택** (상대방)
4. **saju_profiles에서 A, B 간지 조회**
5. **Vector DB에서 궁합 관련 해석 문서 검색 (RAG)**
6. **LLM 프롬프트 생성** (A+B 사주 데이터를 결합한 궁합 분석 요청)
7. **AI 결과 생성**
8. **결과 바로 화면에 반환**
9. **DB 저장 안 함** (서버 부하 및 저장 공간 최적화)

---

