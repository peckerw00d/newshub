from fastapi import APIRouter

from src.app.api.routers.source_admin import router as source_admin_router

router = APIRouter(prefix="/admin", tags=["Admin"])
router.include_router(source_admin_router)
