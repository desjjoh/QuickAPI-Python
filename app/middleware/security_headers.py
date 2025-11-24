from collections.abc import MutableSequence

from starlette.types import ASGIApp, Message, Receive, Scope, Send


class SecurityHeadersMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):

        async def send_wrapper(message: Message):
            if message["type"] == "http.response.start":
                headers: MutableSequence[tuple[bytes, bytes]] = message.setdefault(
                    "headers", []
                )

                def add(name: str, value: str):
                    headers.append((name.encode("latin-1"), value.encode("latin-1")))

                add("X-Content-Type-Options", "nosniff")
                add("X-Frame-Options", "DENY")
                add("Referrer-Policy", "strict-origin-when-cross-origin")
                add("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
                add("X-XSS-Protection", "0")

                add(
                    "Strict-Transport-Security",
                    "max-age=63072000; includeSubDomains; preload",
                )

            await send(message)

        await self.app(scope, receive, send_wrapper)
