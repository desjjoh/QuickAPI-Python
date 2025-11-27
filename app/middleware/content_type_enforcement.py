from __future__ import annotations

from datetime import UTC, datetime

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send


def _now() -> str:
    return datetime.now(UTC).isoformat()


class ContentTypeEnforcementASGIMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        *,
        default_allowed: set[str] | None = None,
        route_overrides: list[tuple[str, set[str]]] | None = None,
    ):
        self.app = app
        self.default_allowed = default_allowed or {"application/json"}
        self.route_overrides = route_overrides or []

        self.no_body_methods = {"GET", "DELETE", "HEAD", "OPTIONS"}

    def _allowed_for_path(self, path: str) -> set[str]:
        for prefix, allowed in self.route_overrides:
            if path.startswith(prefix):
                return allowed

        return self.default_allowed

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = scope.get("method", "").upper()
        path = scope.get("path", "")
        raw_headers = scope.get("headers", [])

        header_map = {k.decode().lower(): v.decode() for k, v in raw_headers}
        content_type = header_map.get("content-type")

        if method in self.no_body_methods:
            if content_type is not None:
                return await self._reject(
                    scope,
                    send,
                    content_type,
                    f"HTTP method '{method}' does not accept a request body.",
                )

            await self.app(scope, receive, send)

            return

        if method in {"POST", "PUT", "PATCH"}:
            allowed: set[str] = self._allowed_for_path(path)

            if content_type is None:
                return await self._reject(
                    scope,
                    send,
                    "<missing>",
                    "Missing Content-Type header.",
                )

            normalized = content_type.split(";")[0].strip().lower()

            if normalized not in allowed:
                return await self._reject(
                    scope,
                    send,
                    content_type,
                    f"Content-Type '{content_type}' is not allowed on this endpoint. "
                    f"Expected one of: {sorted(allowed)}.",
                )

        await self.app(scope, receive, send)

    async def _reject(self, scope: Scope, send: Send, content_type: str, message: str):
        response = JSONResponse(
            status_code=415,
            content={
                "status": 415,
                "message": message,
                "timestamp": _now(),
            },
        )

        async def empty_receive() -> Message:
            return {"type": "http.request", "body": b"", "more_body": False}

        await response(scope, empty_receive, send)
