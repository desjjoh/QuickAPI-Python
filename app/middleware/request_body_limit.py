from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from fastapi import status
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.models.error_model import error_response


async def empty_receive() -> Message:
    return {"type": "http.request", "body": b"", "more_body": False}


def format_bytes_as_mb(value: int) -> str:
    mb: float = value / (1024 * 1024)

    return f"{mb:.2f} MB"


def format_bytes(value: int) -> str:
    if value < 1024:
        return f"{value} B"

    kb = value / 1024
    if kb < 1024:
        return f"{kb:.2f} KB"

    mb = kb / 1024
    if mb < 1024:
        return f"{mb:.2f} MB"

    gb = mb / 1024
    return f"{gb:.2f} GB"


@dataclass(frozen=True)
class BodyLimit:
    max_body_bytes: int = 1_048_576


class RequestBodyLimitASGIMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        *,
        default_limit: BodyLimit,
        route_overrides: Sequence[tuple[str, BodyLimit]] | None = None,
    ):
        self.app = app
        self.default_limit = default_limit
        self.route_overrides = route_overrides or []

    def _select_limit(self, path: str) -> BodyLimit:
        for prefix, override in self.route_overrides:
            if path.startswith(prefix):
                return override

        return self.default_limit

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)

            return

        path: str = scope.get("path", "/")
        limit: BodyLimit = self._select_limit(path)
        max_bytes: int = limit.max_body_bytes

        headers = {k.decode().lower(): v.decode() for k, v in scope.get("headers", [])}
        content_length = headers.get("content-length")

        if content_length is not None:
            try:
                declared: int = int(content_length)

            except ValueError:
                return await self._reject(scope, send, max_bytes)

            if declared > max_bytes:
                return await self._reject(scope, send, max_bytes, used=declared)

        total: int = 0
        body_chunks: list[bytes] = []

        async def limited_receive() -> Message:
            nonlocal total

            message: Message = await receive()

            if message["type"] == "http.request":
                chunk = message.get("body", b"") or b""
                chunk_len: int = len(chunk)

                if chunk_len:
                    total += chunk_len

                    if total > max_bytes:
                        await self._reject(scope, send, max_bytes, used=total)

                        return {"type": "http.disconnect"}

                    body_chunks.append(chunk)

            return message

        async def replay_body() -> Message:
            nonlocal body_chunks

            if body_chunks:
                merged: bytes = b"".join(body_chunks)
                body_chunks = []

                return {"type": "http.request", "body": merged, "more_body": False}

            return await empty_receive()

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                remaining: int = max(max_bytes - total, 0)
                headers = list(message.get("headers", []))

                headers.append((b"x-body-limit-bytes", str(max_bytes).encode()))
                headers.append((b"x-body-remaining-bytes", str(remaining).encode()))

                message["headers"] = headers

            await send(message)

        result: None = await self.app(scope, limited_receive, send_wrapper)
        scope["_body_replay"] = replay_body

        return result

    async def _reject(
        self,
        scope: Scope,
        send: Send,
        max_bytes: int,
        used: int | None = None,
    ):
        used = used or 0

        remaining: int = max(max_bytes - used, 0)
        limit: str = format_bytes(max_bytes)

        response: JSONResponse = error_response(
            status=status.HTTP_413_CONTENT_TOO_LARGE,
            message=f"Request body exceeds maximum allowed size (limit = {limit}).",
            headers={
                "X-Body-Limit-Bytes": str(max_bytes),
                "X-Body-Remaining-Bytes": str(remaining),
            },
        )

        await response(scope, empty_receive, send)
