from fastapi import APIRouter
from app.api.admin.auth import router as auth_router
from app.api.admin.post import router as post_router
from app.api.admin.image import router as image_router
from app.api.admin.account import router as account_router
from app.api.admin.profile import router as profile_router
from app.api.admin.timeline import router as timeline_router
from app.api.admin.product import router as product_router

admin_router = APIRouter(prefix="/admin")

admin_router.include_router(auth_router)
admin_router.include_router(post_router)
admin_router.include_router(image_router)
admin_router.include_router(account_router)
admin_router.include_router(profile_router)
admin_router.include_router(timeline_router)
admin_router.include_router(product_router)
