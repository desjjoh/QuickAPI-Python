import time

from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.config.logging import log


def shorten_path(path: str, max_len: int = 30) -> str:
    if len(path) > max_len:
        return path[: max_len - 1] + "…"
    return path


class RequestLoggingASGIMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        start = time.perf_counter()
        method = scope["method"]
        path = scope["path"]

        async def send_wrapper(message: Message):
            if message["type"] == "http.response.start":
                status = message["status"]
                duration = (time.perf_counter() - start) * 1000
                duration_s = f"{duration:.2f}ms"

                method_padded = method.ljust(7)
                status_padded = str(status).ljust(3)
                path_short = shorten_path(path, 30)
                path_padded = path_short.ljust(32)

                msg = f"{status_padded} {method_padded} {path_padded} {duration_s}"

                level = (
                    "error"
                    if status >= 500
                    else "warning" if status >= 400 else "debug"
                )

                getattr(log, level)(msg)

            await send(message)

        await self.app(scope, receive, send_wrapper)
