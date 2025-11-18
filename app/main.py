import asyncio
import sys

import uvicorn

from app.config.environment import settings

red = "\033[91m"
bold = "\033[1m"


async def bootstrap() -> None:
    try:
        uvicorn.run(
            "app.config.application:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=(settings.ENV == "development"),
            log_config=None,
        )

    except Exception:
        print(
            f"{red}❌ {bold}Fatal error during server initialization — forcing exit\n"
        )
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(bootstrap())
    except Exception:
        print(
            f"{red}❌ {bold}Fatal error during application bootstrap — forcing exit\n"
        )
        sys.exit(1)
