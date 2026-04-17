from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.routers import fortune, profiles

app = FastAPI(
    title="AI 사주 Master API",
    description="이메일 기반 사주 프로필 생성 및 오늘의 운세 제공 서비스",
    version="0.1.0",
)

# ─── 라우터 등록 ───
app.include_router(profiles.router)
app.include_router(fortune.router)


# ─── 공통 에러 핸들러 ───
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "서버 내부 오류가 발생했습니다.",
            }
        },
    )


@app.get("/", tags=["health"])
async def health_check():
    return {"message": "AI 사주 Master 서버에 오신 것을 환영합니다!"}
