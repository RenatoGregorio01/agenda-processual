from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import get_settings
from app.core.database import get_session
from app.core.redis import get_redis
from app.schemas.health import HealthChecks, HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def healthcheck(
    response: Response,
    session: AsyncSession = Depends(get_session),
) -> HealthResponse:
    settings = get_settings()
    db_status = "ok"
    redis_status = "ok"

    try:
        await session.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    redis = await get_redis()
    if redis is None:
        redis_status = "error"
    else:
        try:
            await redis.ping()
        except Exception:
            redis_status = "error"

    overall = "ok" if db_status == "ok" else "error"
    if overall == "ok" and redis_status != "ok":
        overall = "degraded"
    if overall == "error":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return HealthResponse(
        status=overall,
        app=settings.app_name,
        env=settings.app_env,
        checks=HealthChecks(database=db_status, redis=redis_status),
    )
