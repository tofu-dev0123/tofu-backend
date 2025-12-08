from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.security import get_current_user
from app.schemas.post import PostsPostRequest, PostsPostResponse

router = APIRouter(prefix="/posts", tags=["Post 記事関連"])

@router.post("/", response_model=PostsPostResponse)
async def create_posts(request: PostsPostRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return PostsPostResponse(message="", post_id=0)