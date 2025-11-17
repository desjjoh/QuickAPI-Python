import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.app.routes import router as app_router
from app.api.health.routes import router as health_router
from app.api.items.routes import router as items_router
from app.config.database import DatabaseService
from app.config.environment import settings
from app.config.logging import log
from app.exceptions.handlers import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.handlers.lifecycle import lifecycle
from app.middleware.httplogger import RequestLoggingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    name, version, mode = settings.APP_NAME, settings.APP_VERSION, settings.ENV
    pyv = sys.version.split()[0]

    log.info(f"Booting {name} v{version} ({mode}) — Python v{pyv}")

    try:
        lifecycle.register([DatabaseService()])
        await lifecycle.startup()

        port = settings.PORT
        log.info(f"HTTP server running on port {port} at http://localhost:{port}")

        yield
    except Exception:
        log.critical('Unhandled fatal error during server runtime')

        raise
    finally:
        log.warning("Shutdown signal received — beginning shutdown")

        await lifecycle.shutdown()

        log.info("Application exited cleanly")


def create_app() -> FastAPI:
    name = settings.APP_NAME
    version = settings.APP_VERSION

    app = FastAPI(
        title=name,
        version=version,
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


app = create_app()
