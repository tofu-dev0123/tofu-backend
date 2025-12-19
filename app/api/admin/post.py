from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db
from app.core.security import get_current_user
from app.common.message import Message
from app.schemas.post import (
    PostsListGetResponse,
    PostsSummaryResponse,
    PostsPostRequest,
    PostsPutRequest,
    PostsResponse,
    PostGetResponse,
    PostsDeleteResponse,
)
from app.services.post_service import PostService
from app.models.user import User
from app.models.post import PostStatus


router = APIRouter(prefix="/posts", tags=["Post 記事関連"])


def get_post_service(
    db: Session = Depends(get_db),
) -> PostService:
    return PostService(db)


@router.get("/", response_model=PostsListGetResponse)
async def get_posts(
    keyword: Optional[str] = Query(None, max_length=1000),
    status: Optional[PostStatus] = Query(None),
    offset: Optional[int] = Query(0, ge=0),
    limit: Optional[int] = Query(10, ge=1, le=30),
    service: PostService = Depends(get_post_service),
    current_user: User = Depends(get_current_user),
):
    user_id = current_user.user_id

    result = service.get_posts(user_id, offset, limit, keyword, status)

    return result


@router.post("/", response_model=PostsResponse)
async def create_posts(
    request: PostsPostRequest,
    service: PostService = Depends(get_post_service),
    current_user: User = Depends(get_current_user),
):
    try:
        new_post_id = service.create_all(request, current_user.user_id)

    except:
        raise

    return PostsResponse(message=Message.POST_CREATE_SUCCESS, post_id=new_post_id)


@router.get("/summary", response_model=PostsSummaryResponse)
async def get_summary(
    service: PostService = Depends(get_post_service),
    current_user: User = Depends(get_current_user),
):
    summary = service.get_summary()

    return PostsSummaryResponse(**summary._mapping)


@router.get("/{post_id}", response_model=PostGetResponse)
async def get_post(
    post_id: int = Path(..., ge=1, description="記事ID"),
    service: PostService = Depends(get_post_service),
    current_user: User = Depends(get_current_user),
):
    data = service.get_post_detail(post_id)

    return data


@router.put("/{post_id}", response_model=PostsResponse)
async def update_post(
    request: PostsPutRequest,
    post_id: int = Path(..., ge=1, description="記事ID"),
    service: PostService = Depends(get_post_service),
    current_user: User = Depends(get_current_user),
):
    service.update_all(request, post_id)

    return PostsResponse(message=Message.POST_UPDATE_SUCCESS, post_id=post_id)


@router.delete("/{post_id}", response_model=PostsDeleteResponse)
async def delete_post(
    post_id: int = Path(..., ge=1, description="記事ID"),
    service: PostService = Depends(get_post_service),
    current_user: User = Depends(get_current_user),
):
    service.delete_all(post_id)

    return PostsDeleteResponse(message=Message.POST_DELETE_SUCCESS)
