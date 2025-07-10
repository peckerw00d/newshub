from fastapi import APIRouter

from src.app.api.routers.admin.source import router as source_admin_router
from src.app.api.routers.news import router as news_router

router = APIRouter(
    prefix="/api",
)
router.include_router(source_admin_router)
router.include_router(news_router)
