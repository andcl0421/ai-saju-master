## 1. 사주 만세력 계산 (Calculate Saju Ganji)
- **Method:** `POST`
- **Endpoint:** `/api/v1/saju/calculate`
- **Description:** 입력된 생년월일시를 바탕으로 사주 팔자(간지)를 계산합니다. 생시를 모를 경우 정오(12:00)로 보정합니다.

### [코드 예시 - Python/FastAPI]
```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, time

router = APIRouter(prefix="/api/v1/saju", tags=["Saju"])

# 1. 요청 데이터 모델 (Request Schema)
class SajuRequest(BaseModel):
    user_email: EmailStr
    birth_date: str  # YYYY-MM-DD
    birth_time: str  # HH:MM 또는 'UNKNOWN'
    gender: str      # MALE, FEMALE
    calendar_type: str # SOLAR, LUNAR

# 2. 응답 데이터 모델 (Response Schema)
class SajuResponse(BaseModel):
    year_ganji: str
    month_ganji: str
    day_ganji: str
    time_ganji: str
    calculated_birth_time: str
    is_time_unknown: bool

@router.post("/calculate", response_model=SajuResponse)
async def calculate_saju_ganji(request: SajuRequest):
    """
    사용자의 생년월일시를 받아 만세력 간지를 반환합니다.
    """
    
    # [비즈니스 로직 1] 생시 보정 (UNKNOWN 처리)
    target_time = request.birth_time
    is_unknown = False
    
    if target_time.upper() == "UNKNOWN":
        target_time = "12:00"  # 도메인 규칙: 모를 경우 정오로 보정
        is_unknown = True
    
    try:
        # [비즈니스 로직 2] 실제 만세력 계산 호출 (예시 함수)
        # 실제 구현 시에는 korean_lunar_calendar 같은 라이브러리나 
        # 직접 구현한 만세력 변환 함수(convert_to_ganji)를 사용합니다.
        ganji_result = dummy_mansae_engine(
            request.birth_date, 
            target_time, 
            request.calendar_type
        )
        
        return {
            "year_ganji": ganji_result["year"],
            "month_ganji": ganji_result["month"],
            "day_ganji": ganji_result["day"],
            "time_ganji": ganji_result["hour"],
            "calculated_birth_time": target_time,
            "is_time_unknown": is_unknown
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"만세력 계산 중 오류 발생: {str(e)}")

# 임시 만세력 엔진 (실제 로직으로 대체 필요)
def dummy_mansae_engine(b_date, b_time, c_type):
    # 이 부분에 실제 육십갑자 변환 로직이 들어갑니다.
    return {
        "year": "갑자(甲子)",
        "month": "을축(乙丑)",
        "day": "병인(丙寅)",
        "hour": "정묘(丁卯)"
    }
```