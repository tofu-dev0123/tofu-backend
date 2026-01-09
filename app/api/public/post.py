from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session
from typing import Optional
from app.schemas.post import (
    PostsPublishAtResponse,
)
from app.services.public.post_service import PublicPostService
from app.db.database import get_db


router = APIRouter(prefix="/posts", tags=["Post 公開記事関連"])


def get_post_service(
    db: Session = Depends(get_db),
) -> PublicPostService:
    return PublicPostService(db)


@router.get("/", response_model=PostsPublishAtResponse)
async def get_posts(
    page: Optional[int] = Query(1, ge=1),
    keyword: Optional[str] = Query(None, max_length=1000),
    service: PublicPostService = Depends(get_post_service),
):

    if page is None:
        page = 1

    result = service.get_posts(page, keyword)
    return result
