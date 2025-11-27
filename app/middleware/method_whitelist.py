from __future__ import annotations

from fastapi import status
from fastapi.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.models.error_model import error_response


class MethodWhitelistASGIMiddleware:
    def __init__(self, app: ASGIApp, allowed_methods: set[str]):
        self.app = app
        self.allowed_methods = {m.upper() for m in allowed_methods}

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)

            return

        method = scope.get("method", "").upper()

        if method not in self.allowed_methods:
            return await self._reject(scope, send, method)

        await self.app(scope, receive, send)

    async def _reject(self, scope: Scope, send: Send, method: str):
        response: JSONResponse = error_response(
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
            message=f"HTTP method '{method}' is not allowed on this server.",
        )

        async def empty_receive() -> Message:
            return {"type": "http.request", "body": b"", "more_body": False}

        await response(scope, empty_receive, send)
