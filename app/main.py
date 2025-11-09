import asyncio
import signal
import sys
import traceback

import uvicorn

from app.core.config import settings
from app.core.logging import log, setup_logging
from app.helpers.db import close_db, init_db
from app.helpers.lifecycle import LifecycleManager


async def bootstrap() -> None:
    setup_logging()

    log.info("Starting QuickAPI — FastAPI...")
    log.info(f"  ↳ Python {sys.version.split()[0]} initialized")

    lifecycle = LifecycleManager()

    config = uvicorn.Config(
        "app.helpers.app:create_app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        factory=True,
        access_log=False,
    )

    server = uvicorn.Server(config)

    try:
        await init_db()
        lifecycle.register("database", close_db)
        log.info("  ↳ Database initialized")

        await server.serve()
    except Exception as e:
        log.critical(
            "Fatal error during initialization",
            error=repr(e),
            traceback=traceback.format_exc(),
        )
        sys.exit(1)
    finally:
        await lifecycle.shutdown(signal.Signals.SIGINT)


if __name__ == "__main__":
    asyncio.run(bootstrap())
