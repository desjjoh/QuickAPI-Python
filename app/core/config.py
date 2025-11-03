"""
config.py
----------
Centralized application configuration using Pydantic settings management.

Handles environment variable parsing and type validation for core service
configuration fields such as application name, version, and debug mode.

✅ Automatically loads environment variables from a `.env` file.
✅ Provides runtime type safety and defaults for all key settings.
✅ Consistent with `Zod`-based env validation in Node/TypeScript projects.

This module should serve as the single source of truth for environment-driven
configuration values.

"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Global application settings.

    Defines strongly typed configuration values automatically populated
    from environment variables or a `.env` file in the project root.

    Attributes:
        app_name (str):
            The name of the application. Defaults to `"QuickAPI"`.
        version (str):
            The current service version string. Defaults to `"1.0.0"`.
        debug (bool):
            Enables verbose logging and development behavior when `True`.

    Example:
        ```python
        from app.core.config import settings

        if settings.debug:
            print(f"Running {settings.app_name} v{settings.version} in debug mode")
        ```
    """

    app_name: str = "QuickAPI"
    version: str = "1.0.0"
    debug: bool = True

    class Config:
        """
        Pydantic settings configuration.

        Specifies the source for environment variables and enables automatic
        loading from a `.env` file when present.
        """
        env_file = ".env"


# Instantiate the global settings object
settings = Settings()
"""
Global configuration instance.

Example:
    ```python
    from app.core.config import settings
    print(settings.app_name)
    ```
"""
