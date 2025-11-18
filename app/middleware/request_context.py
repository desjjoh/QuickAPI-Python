# import uuid
# from collections.abc import Awaitable, Callable

# import structlog
# from fastapi import Request, Response
# from starlette.middleware.base import BaseHTTPMiddleware

# from app.store.request_context import RequestContext, RequestContextData

# RequestResponseEndpoint = Callable[[Request], Awaitable[Response]]


# class RequestContextMiddleware(BaseHTTPMiddleware):

#     async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
#         request_id = uuid.uuid4().hex[:8]

#         ctx = RequestContextData(
#             request_id=request_id,
#             method=request.method,
#             path=request.url.path,
#             ip=request.client.host if request.client else "unknown",
#         )

#         structlog.contextvars.bind_contextvars(
#             request_id=request_id,
#             method=request.method,
#             path=request.url.path,
#             ip=request.client.host if request.client else "unknown",
#         )

#         RequestContext.set(ctx)

#         try:
#             response = await call_next(request)
#             return response
#         finally:
#             RequestContext.clear()

import uuid

import structlog
from starlette.types import ASGIApp, Receive, Scope, Send

from app.store.request_context import RequestContext, RequestContextData


class RequestContextMiddleware:

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        request_id = uuid.uuid4().hex[:8]
        method = scope["method"]
        path = scope["path"]
        client = scope.get("client", ["unknown"])[0]

        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=method,
            path=path,
            ip=client,
        )

        scope["ctx"] = {
            "request_id": request_id,
            "method": method,
            "path": path,
            "ip": client,
        }

        ctx = RequestContextData(
            request_id=request_id,
            method=method,
            path=path,
            ip=client,
        )

        RequestContext.set(ctx)

        try:
            await self.app(scope, receive, send)
        finally:
            structlog.contextvars.clear_contextvars()
