from __future__ import annotations

from dataclasses import dataclass

from fastapi import status
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.models.error_model import error_response


@dataclass(frozen=True)
class HeaderLimits:
    max_header_count: int = 100
    max_single_header_bytes: int = 4_096
    max_total_header_bytes: int = 8_192
    allow_chunked: bool = False


class RequestHeaderLimitASGIMiddleware:
    def __init__(self, app: ASGIApp, limits: HeaderLimits = HeaderLimits()):
        self.app = app
        self.limits = limits

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)

            return

        raw_headers = scope.get("headers", [])

        if len(raw_headers) > self.limits.max_header_count:
            return await self._reject(
                scope,
                send,
                status_code=status.HTTP_431_REQUEST_HEADER_FIELDS_TOO_LARGE,
                message=f"Too many headers (limit = {self.limits.max_header_count}).",
            )

        total_bytes: int = 0

        for key, value in raw_headers:
            size: int = len(key) + len(value)
            total_bytes += size

            if size > self.limits.max_single_header_bytes:
                return await self._reject(
                    scope,
                    send,
                    status_code=status.HTTP_431_REQUEST_HEADER_FIELDS_TOO_LARGE,
                    message=f"Header exceeds per-header size limit ({self.limits.max_single_header_bytes} bytes).",
                )

        if total_bytes > self.limits.max_total_header_bytes:
            return await self._reject(
                scope,
                send,
                status_code=status.HTTP_431_REQUEST_HEADER_FIELDS_TOO_LARGE,
                message=f"Total header size exceeds limit ({self.limits.max_total_header_bytes} bytes).",
            )

        headers_map = {k.decode().lower(): v.decode() for k, v in raw_headers}
        transfer = headers_map.get("transfer-encoding")

        if not self.limits.allow_chunked and transfer:
            if "chunked" in transfer.lower():
                return await self._reject(
                    scope,
                    send,
                    status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                    message="Chunked request bodies are not allowed.",
                )

        await self.app(scope, receive, send)

    async def _reject(
        self, scope: Scope, send: Send, *, status_code: int, message: str
    ):
        response: JSONResponse = error_response(
            status=status_code,
            message=message,
        )

        async def empty_receive() -> Message:
            return {"type": "http.request", "body": b"", "more_body": False}

        await response(scope, empty_receive, send)
