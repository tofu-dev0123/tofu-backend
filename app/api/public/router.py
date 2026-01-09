from fastapi import APIRouter
from app.api.public.post import router as post_router

public_router = APIRouter()

public_router.include_router(post_router)
