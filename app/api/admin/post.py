from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.security import get_current_user
from app.common.message import Message
from app.schemas.post import PostsPostRequest, PostsPostResponse
from app.services.post_service import PostService
from app.models.user import User

router = APIRouter(prefix="/posts", tags=["Post 記事関連"])


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
