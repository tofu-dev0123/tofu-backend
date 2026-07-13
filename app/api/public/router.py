from fastapi import APIRouter
from app.api.public.post import router as post_router
from app.api.public.about import router as about_router
from app.api.public.product import router as product_router

public_router = APIRouter()

public_router.include_router(post_router)
public_router.include_router(about_router)
public_router.include_router(product_router)
