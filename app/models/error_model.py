from datetime import UTC, datetime

from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    status: int = Field(..., description="HTTP status code", examples=[503])

    message: str = Field(
        ...,
        description="Human-readable error message",
        examples=["Application not ready."],
    )

    timestamp: int = Field(
        ...,
        description="Unix timestamp in milliseconds.",
        examples=[1_764_281_029],
    )


def error_response(
    status: int,
    message: str,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    ts_ms = int(datetime.now(UTC).timestamp() * 1000)

    model = ErrorResponse(
        status=status,
        message=message,
        timestamp=ts_ms,
    )

    return JSONResponse(
        status_code=status,
        content=model.model_dump(),
        headers=headers or {},
    )
