from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.routers import fortune, profiles, system

app = FastAPI(
    title="AI Saju Master API",
    description="Email-based saju profile and daily fortune service.",
    version="0.2.0",
)

app.include_router(profiles.router)
app.include_router(fortune.router)
app.include_router(system.router)


@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "status": 500,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected server error occurred.",
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": str(request.url.path),
        },
    )


@app.get("/", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"message": "AI Saju Master API is running."}
