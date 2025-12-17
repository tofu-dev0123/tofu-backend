from fastapi import APIRouter
from app.api.admin.auth import router as auth_router
from app.api.admin.post import router as post_router
from app.api.admin.image import router as image_router

admin_router = APIRouter(prefix="/admin")

admin_router.include_router(auth_router)
admin_router.include_router(post_router)
admin_router.include_router(image_router)
