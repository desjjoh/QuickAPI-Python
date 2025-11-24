from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def configure_custom_validation_openapi(app: FastAPI) -> None:
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        schema = get_openapi(
            title=app.title,
            version=app.version,
            routes=app.routes,
        )

        schema["components"]["schemas"]["ValidationError"] = {
            "type": "object",
            "properties": {
                "status": {"type": "integer", "example": 422},
                "message": {
                    "type": "string",
                    "example": "Validation failed: name → Field required; path.id → String should have at least 16 characters",
                },
                "timestamp": {"type": "string", "format": "date-time"},
            },
            "required": ["status", "message", "timestamp"],
        }

        schema["components"]["schemas"]["HTTPValidationError"] = {
            "type": "object",
            "properties": {
                "status": {"type": "integer", "example": 422},
                "message": {
                    "type": "string",
                    "example": "Validation failed: name → Field required; path.id → String should have at least 16 characters",
                },
                "timestamp": {"type": "string", "format": "date-time"},
            },
            "required": ["status", "message", "timestamp"],
        }

        app.openapi_schema = schema
        return app.openapi_schema

    app.openapi = custom_openapi
