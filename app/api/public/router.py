from fastapi import APIRouter, Depends
from app.api.public.cache import set_public_cache
from app.api.public.post import router as post_router
from app.api.public.about import router as about_router
from app.api.public.product import router as product_router

# 公開 API は全エンドポイントに CDN キャッシュ用ヘッダを付与する
public_router = APIRouter(dependencies=[Depends(set_public_cache)])

public_router.include_router(post_router)
public_router.include_router(about_router)
public_router.include_router(product_router)
