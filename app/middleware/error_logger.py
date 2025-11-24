from starlette.types import ASGIApp, Receive, Scope, Send

from app.config.logging import log


class ErrorLoggingASGIMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        try:
            await self.app(scope, receive, send)

        except Exception as exc:
            error_type = exc.__class__.__name__
            error_msg = getattr(exc, "msg", None) or str(exc).split("\n")[0]

            log.error(f"{error_type}: {error_msg}")

            raise
