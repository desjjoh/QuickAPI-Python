import logging
from typing import Any, Protocol

import structlog
from colorama import Fore, Style
from structlog.typing import EventDict, WrappedLogger


class LoggerProtocol(Protocol):
    def trace(self, event: str, **kwargs: Any) -> None: ...
    def debug(self, event: str, **kwargs: Any) -> None: ...
    def info(self, event: str, **kwargs: Any) -> None: ...
    def warning(self, event: str, **kwargs: Any) -> None: ...
    def error(self, event: str, **kwargs: Any) -> None: ...
    def critical(self, event: str, **kwargs: Any) -> None: ...


def setup_logging() -> None:
    logging.basicConfig(format="%(message)s", level=logging.INFO)

    for noisy in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
        logging.getLogger(noisy).handlers = []
        logging.getLogger(noisy).propagate = False
        logging.getLogger(noisy).setLevel(logging.WARNING)

    colors = {
        "INFO": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": Fore.MAGENTA,
    }

    dark_green = '\x1b[2m\x1b[32m'

    def concise_renderer(_: WrappedLogger, __: str, event_dict: EventDict) -> str:
        timestamp = event_dict.pop("timestamp", "")
        level = event_dict.pop("level", "")
        message = event_dict.pop("event", "")
        color = colors.get(level.upper(), Fore.WHITE)
        reset = Style.RESET_ALL

        extras = " ".join(
            f"{Fore.BLUE}{k}{reset}{Style.DIM}={v}{reset}"
            for k, v in event_dict.items()
            if v is not None
        )

        line = f"{dark_green}{timestamp}{reset} {color}[{level}]{reset} {message}"

        if extras:
            line += f" {extras}{reset}"

        return line

    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S.%f", utc=False),
            concise_renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


log: LoggerProtocol = structlog.get_logger()
