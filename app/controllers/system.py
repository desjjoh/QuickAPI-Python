import time

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.config.database import get_session
from app.config.environment import settings
from app.models.system import HealthOut, MetricsOut

router = APIRouter(tags=["System"])
_start_time = time.perf_counter()


@router.get("/", summary="Root endpoint", response_model=dict[str, str])
async def root() -> dict[str, str]:
    return {"message": "Hello World! Welcome to FastAPI!"}


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
        uptime_seconds=uptime, app=settings.APP_NAME, version="1.0.0", debug=True
    )
