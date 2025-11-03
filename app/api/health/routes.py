"""
api/system/routes.py
--------------------
System health and metrics endpoints for the QuickAPI FastAPI service.

Implements standardized operational probes for liveness, readiness, and runtime metrics.
Endpoints are lightweight, dependency-aware, and suitable for integration with
Docker or Kubernetes health checks.
"""

import time
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from app.core.logging import log
from app.services.db import get_session
from app.api.health.models.schemas import HealthOut, MetricsOut
from app.core.config import settings

router = APIRouter(prefix="/health", tags=["Health"])

# Track application uptime
_start_time = time.perf_counter()


@router.get("/live", response_model=HealthOut, status_code=status.HTTP_200_OK)
async def live_probe() -> HealthOut:
    """
    Liveness probe endpoint.

    Returns:
        HealthOut: Indicates whether the application process is alive.
    """
    log.debug("Liveness check triggered")
    return HealthOut(status="alive")


@router.get("/ready", response_model=HealthOut)
async def ready_probe() -> JSONResponse:
    """
    Readiness probe endpoint.

    Performs a minimal database query to verify connectivity.
    Returns HTTP 200 if ready, or HTTP 503 if a dependency is unavailable.
    """
    async for db in get_session():
        try:
            await db.execute(text("SELECT 1"))
            log.debug("Readiness check successful", db_status="ok")
            return JSONResponse(status_code=200, content=HealthOut(status="ready").model_dump())
        except Exception as e:
            log.warning("Readiness check failed", error=str(e))
            return JSONResponse(
                status_code=503,
                content=HealthOut(status="unhealthy", error=str(e)).model_dump(),
            )


@router.get("/metrics", response_model=MetricsOut)
async def system_metrics() -> MetricsOut:
    """
    Basic runtime metrics endpoint.

    Returns:
        MetricsOut: Includes uptime, app name, version, and debug flag.
    """
    uptime = time.perf_counter() - _start_time
    log.debug("Metrics requested", uptime=uptime)
    return MetricsOut(
        uptime_seconds=uptime,
        app=settings.app_name,
        version="1.0.0",
        debug=settings.debug,
    )
