from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.app.routes import router as app_router
from app.api.health.routes import router as health_router
from app.api.items.routes import router as items_router
from app.core.config import settings
from app.core.handlers import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.core.logging import log
from app.core.middleware import RequestLoggingMiddleware

mode = 'development' if settings.debug else 'production'


@asynccontextmanager
async def lifespan(_: object) -> AsyncIterator[None]:
    log.info(f"  ↳ HTTP server running in {mode} mode at http://localhost:8000")
    log.info("  ↳ API documentation available at http://localhost:8000/docs")
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        lifespan=lifespan,
    )

    app.include_router(app_router)
    app.include_router(items_router)
    app.include_router(health_router)

    app.exception_handler(RequestValidationError)(validation_exception_handler)
    app.exception_handler(StarletteHTTPException)(http_exception_handler)
    app.exception_handler(Exception)(unhandled_exception_handler)

    app.add_middleware(RequestLoggingMiddleware)

    return app
