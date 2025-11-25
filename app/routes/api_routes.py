from fastapi import APIRouter

from app.routes.v1_routes import router as v1_router

router: APIRouter = APIRouter(prefix="/api")

router.include_router(v1_router)
