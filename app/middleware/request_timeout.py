from __future__ import annotations

import asyncio

from starlette.types import ASGIApp, Message, Receive, Scope, Send


class RequestTimeoutASGIMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        header_timeout: float = 5.0,
        chunk_timeout: float = 2.0,
        total_timeout: float = 10.0,
    ):
        self.app = app
        self.header_timeout = header_timeout
        self.chunk_timeout = chunk_timeout
        self.total_timeout = total_timeout

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)

            return

        start_time: float = asyncio.get_event_loop().time()
        received_headers: bool = False

        async def timed_receive() -> Message:
            nonlocal received_headers
            now: float = asyncio.get_event_loop().time()

            if not received_headers:
                time_elapsed: float = now - start_time

                if time_elapsed > self.header_timeout:
                    return _timeout_disconnect()

            try:
                message: Message = await asyncio.wait_for(
                    receive(),
                    timeout=(
                        self.chunk_timeout if received_headers else self.header_timeout
                    ),
                )

            except TimeoutError:
                return _timeout_disconnect()

            if message["type"] == "http.request":
                received_headers = True

                total_elapsed: float = now - start_time

                if total_elapsed > self.total_timeout:
                    return _timeout_disconnect()

            return message

        def _timeout_disconnect() -> Message:
            return {"type": "http.disconnect"}

        await self.app(scope, timed_receive, send)
