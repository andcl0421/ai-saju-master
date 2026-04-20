from __future__ import annotations

import os
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db

router = APIRouter(prefix="/api/v1/system", tags=["system"])


@router.get("/health")
async def system_health(
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    try:
        await db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Database is unavailable.") from exc

    return {
        "status": 200,
        "data": {
            "api_server": "ALIVE",
            "database": "CONNECTED",
            "ai_engine": "READY" if os.getenv("OPENAI_API_KEY") else "CONFIG_REQUIRED",
            "last_check_at": datetime.now(timezone.utc).isoformat(),
        },
    }
