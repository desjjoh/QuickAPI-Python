from fastapi import APIRouter

router = APIRouter(tags=["System"])


@router.get("/", summary="Root endpoint", response_model=dict[str, str])
async def root() -> dict[str, str]:
    return {"message": "Hello from FastAPI!"}
