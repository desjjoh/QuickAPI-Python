import time

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.health.models.schemas import HealthOut, MetricsOut
from app.core.config import settings
from app.helpers.db import get_session

router = APIRouter(prefix="/health", tags=["Health"])
_start_time = time.perf_counter()


@router.get("/live", response_model=HealthOut, status_code=status.HTTP_200_OK)
async def live_probe() -> HealthOut:
    return HealthOut(status="alive", error=None)


@router.get("/ready", response_model=HealthOut)
async def ready_probe() -> JSONResponse:
    async for db in get_session():
        try:
            await db.execute(text("SELECT 1"))
            return JSONResponse(
                status_code=200,
                content=HealthOut(status="ready", error=None).model_dump(),
            )
        except Exception as e:
            return JSONResponse(
                status_code=503,
                content=HealthOut(status="unhealthy", error=str(e)).model_dump(),
            )

    return JSONResponse(
        status_code=503,
        content=HealthOut(
            status="unhealthy", error="Database session unavailable"
        ).model_dump(),
    )


@router.get("/metrics", response_model=MetricsOut)
async def system_metrics() -> MetricsOut:
    uptime = time.perf_counter() - _start_time
    return MetricsOut(
        uptime_seconds=uptime,
        app=settings.app_name,
        version="1.0.0",
        debug=settings.debug,
    )
