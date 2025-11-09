import asyncio
import signal
import sys
import time
from collections.abc import Awaitable, Callable

from app.core.logging import log

ShutdownFn = Callable[[], Awaitable[None]]


class LifecycleManager:

    def __init__(self) -> None:
        self._services: list[tuple[str, ShutdownFn]] = []
        self._shutdown_started = False

    def register(self, name: str, stop: ShutdownFn) -> None:
        self._services.append((name, stop))

    async def shutdown(self, sig: signal.Signals | None = None) -> None:
        if self._shutdown_started:
            return
        self._shutdown_started = True

        started = time.perf_counter()

        if sig:
            log.warning(f"{sig.name} received — initiating graceful shutdown...")
        else:
            log.warning("Initiating graceful shutdown...")

        for name, stop in self._services:
            try:
                log.info(f"  ↳ stopping service → {name}")
                asyncio.shield(stop())
            except asyncio.CancelledError:
                log.warning(f"  ↳ cancellation while stopping service → {name}")
            except Exception:
                log.critical("Failed to stop service")
                sys.exit(1)

        log.info("  ↳ stopping service → FastAPI")

        duration = (time.perf_counter() - started) * 1000

        log.info(f"Shutdown complete ({duration:.2f}ms)")
        sys.exit(0)
