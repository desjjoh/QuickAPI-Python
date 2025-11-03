"""
logging.py
-----------
Centralized structured logging configuration.

Integrates the standard library `logging` module with `structlog` to provide
contextual, structured, and colorized logging for FastAPI services.

✅ Structured logs suitable for JSON ingestion or console readability.
✅ Color-coded log levels for local development.
✅ Timestamped, concise single-line output format.

This configuration aligns with the Lumina logging philosophy:
fail fast, leave a trail, and communicate context clearly.

"""

import logging
import structlog
from colorama import Fore, Style
from app.core.config import settings


def setup_logging() -> None:
    """
    Configure the global logging system.

    Initializes both the standard library `logging` and `structlog` to produce
    clean, contextual logs. The configuration applies colorized, single-line
    log entries suitable for both interactive development and production logs
    when piped to a collector.

    Behavior:
        - Adds timestamps and log levels automatically.
        - Applies level-based color formatting for readability.
        - Structures remaining context as key/value pairs.

    Returns:
        None
    """
    # Initialize basic Python logging to ensure structlog hooks are active
    logging.basicConfig(format="%(message)s", level=logging.INFO)

    # Color palette for terminal readability
    COLORS = {
        "INFO": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "DEBUG": Fore.CYAN,
    }

    def concise_renderer(_: dict, __: str, event_dict: dict) -> str:
        """
        Custom renderer for concise, colorized log output.

        Args:
            _ (dict): Unused positional argument from structlog.
            __ (str): Logger name (unused).
            event_dict (dict): Event data dictionary containing the log fields.

        Returns:
            str: Formatted and colorized log string.
        """
        timestamp = event_dict.pop("timestamp", "")
        level = event_dict.pop("level", "").upper()
        message = event_dict.pop("event", "")
        extras = " ".join(f'"{k}":{repr(v)}' for k, v in event_dict.items())

        color = COLORS.get(level, Fore.WHITE)
        message_color = Fore.CYAN
        reset = Style.RESET_ALL

        return (
            f"[{timestamp}]{reset} "
            f"{color}{level:<5}{reset}: "
            f"{message_color}{message}{reset} "
            f"{Style.DIM}{{{extras}}}{reset}"
        )

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,  # Attach log level to events
            structlog.processors.TimeStamper(fmt="%H:%M:%S.%f", utc=False),  # Timestamp
            concise_renderer,  # Final renderer (console output)
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


# Global shared logger instance
log = structlog.get_logger()
"""
The primary shared logger instance for the application.

Example:
    ```python
    from app.core.logging import log

    log.info("Server started", port=8000)
    log.error("Database connection failed", db_url="sqlite:///app.db")
    ```
"""
