"""
core/middleware.py
--------------
Request lifecycle logging middleware.

Intercepts all incoming HTTP requests and outgoing responses to provide
structured contextual logging, including execution duration, status codes,
and unhandled exceptions.

✅ Captures both success and failure paths.
✅ Measures duration using high-precision `perf_counter`.
✅ Ensures JSON-formatted error response on unhandled exceptions.

"""

import time
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import log


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for structured request/response logging.

    Logs essential request metadata including HTTP method, path,
    response status, and total duration in milliseconds.

    In the event of an unhandled exception within the request pipeline,
    the middleware logs the error and returns a standardized 500 response.

    Attributes:
        None

    Example:
        ```python
        from fastapi import FastAPI
        from app.core.middleware import RequestLoggingMiddleware

        app = FastAPI()
        app.add_middleware(RequestLoggingMiddleware)
        ```
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Intercept each incoming HTTP request for logging.

        Args:
            request (Request):
                The incoming FastAPI `Request` object.
            call_next (Callable):
                The next handler in the request chain.

        Returns:
            Response:
                The FastAPI `Response` object after processing.

        Behavior:
            - Logs the request method, path, status, and duration.
            - Logs exceptions as structured errors and returns a JSON 500.
        """
        start_time = time.perf_counter()

        try:
            # Proceed with request
            response: Response = await call_next(request)
        except Exception as exc:
            duration = (time.perf_counter() - start_time) * 1000
            log.error(
                "Unhandled exception during request",
                method=request.method,
                path=request.url.path,
                error=str(exc),
                ms=round(duration, 2),
            )

            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"},
            )

        # Log completion metrics
        duration = (time.perf_counter() - start_time) * 1000
        log.info(
            "Request completed",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            ms=round(duration, 2),
        )
        return response
