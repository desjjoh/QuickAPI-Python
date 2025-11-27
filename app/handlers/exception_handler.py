from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.models.error_model import error_response


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    return error_response(status=exc.status_code, message=exc.detail)


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    status_code: int = status.HTTP_422_UNPROCESSABLE_CONTENT
    parts: list[str] = []

    for error in exc.errors():
        loc = error["loc"]
        msg: str = error["msg"]

        if loc == ("body",) or (
            len(loc) == 2 and loc[0] == "body" and isinstance(loc[1], (int, str))
        ):
            parts.append(f"Request body → {msg}")
            continue

        loc_parts: list[str] = [str(p) for p in loc if p not in ("body", None, "", ())]
        field_path: str = ".".join(loc_parts)

        if field_path:
            parts.append(f"{field_path} → {msg}")

        else:
            parts.append(msg)

    message: str = "Validation failed: " + "; ".join(parts) + '.'

    return error_response(status=status_code, message=message)


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    return error_response(status=status_code, message="Internal server error.")
