from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.db.database import get_db
from app.core.security import get_current_user
from app.common.message import Message
from app.schemas.post import Post, PostsGetResponse, PostsPostRequest, PostsPostResponse
from app.services.post_service import PostService
from app.models.user import User

router = APIRouter(prefix="/posts", tags=["Post 記事関連"])


@router.get("/", response_model=PostsGetResponse)
async def get_posts(
    keyword: Optional[str] = Query(None, max_length=1000),
    offset: Optional[int] = Query(0, ge=0),
    limit: Optional[int] = Query(10, ge=1, le=30),
    db: Session = Depends(get_db),
):
    return PostsGetResponse(
        total_count=1,
        total_pages=1,
        posts=[
            Post(
                post_id=1,
                user_id=1,
                title="タイトル",
                slug="slug",
                thumbnail_url="http://test.com",
                status="DRAFT",
                publishedAt=datetime.now(),
                createdAt=datetime.now(),
                updatedAt=datetime.now(),
            )
        ]
    )


@router.post("/", response_model=PostsPostResponse)
async def create_posts(
    request: PostsPostRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = PostService(db)

    try:
        new_post_id = service.create_all(request, current_user.user_id)

    except:
        raise

    return PostsPostResponse(message=Message.POST_CREATE_SUCCESS, post_id=new_post_id)
