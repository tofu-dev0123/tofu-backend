from fastapi import APIRouter, Depends, Query, Path
from typing import Optional
from app.schemas.post import (
    PostsPublishAtResponse,
    PostPublishAtResponse,
    PostSlugsResponse,
)
from app.services.public.post_service import PublicPostService
from app.api.deps import get_public_post_service
from app.common.constant import Constant


router = APIRouter(prefix="/posts", tags=["Post 公開記事関連"])


@router.get("", response_model=PostsPublishAtResponse)
def get_posts(
    page: Optional[int] = Query(Constant.MIN_PAGE, ge=Constant.MIN_PAGE),
    keyword: Optional[str] = Query(None, max_length=Constant.MAX_KEYWORD_LENGTH),
    service: PublicPostService = Depends(get_public_post_service),
) -> PostsPublishAtResponse:

    if page is None:
        page = 1

    result = service.get_posts(page, keyword)
    return result


@router.get("/slugs", response_model=PostSlugsResponse)
def get_slugs(
    service: PublicPostService = Depends(get_public_post_service),
) -> PostSlugsResponse:
    result = service.get_slugs()
    return result


@router.get("/{slug}", response_model=PostPublishAtResponse)
def get_post(
    slug: str = Path(..., description="スラグ"),
    service: PublicPostService = Depends(get_public_post_service),
) -> PostPublishAtResponse:
    result = service.get_post(slug)
    return result
