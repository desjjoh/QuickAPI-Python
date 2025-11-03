"""
api/system/models/schemas.py
----------------------------
Pydantic response models for system health and metrics endpoints.

These models formalize operational data contracts so that
FastAPI’s OpenAPI documentation can render complete, typed schemas.
"""

from pydantic import BaseModel, Field
from typing import Optional


class HealthOut(BaseModel):
    """Represents the response structure for health and readiness probes."""

    status: str = Field(..., description="Current status of the service (alive, ready, unhealthy).")
    error: Optional[str] = Field(None, description="Optional error detail if status is unhealthy.")


class MetricsOut(BaseModel):
    """Represents basic runtime metrics for observability."""

    uptime_seconds: float = Field(..., description="Seconds since application startup.")
    app: str = Field(..., description="Application name.")
    version: str = Field(..., description="Build or release version string.")
    debug: bool = Field(..., description="Indicates whether the app is running in debug mode.")
