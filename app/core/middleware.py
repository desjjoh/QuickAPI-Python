import time
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import log


class RequestLoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        start_time = time.perf_counter()

        method = request.method
        path = request.url.path

        response: Response = await call_next(request)

        duration_ms = (time.perf_counter() - start_time) * 1000
        duration = f"{duration_ms:.2f}ms"

        status = response.status_code
        level = "error" if status >= 500 else "warning" if status >= 400 else "info"

        getattr(log, level)(f"{method} {path} {status} → {duration}")

        return response
