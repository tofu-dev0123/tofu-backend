from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.security import get_current_user
from app.core.exceptions.post_exceptions import ImageNotExistError
from app.schemas.post import PostsPostRequest, PostsPostResponse
from app.services.post_service import check_image_list

router = APIRouter(prefix="/posts", tags=["Post 記事関連"])

@router.post("/", response_model=PostsPostResponse)
async def create_posts(request: PostsPostRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # 画像IDの存在チェック
    try:
        check_image_list(request.images)
    
    except ImageNotExistError:
        raise
    
    return PostsPostResponse(message="", post_id=0)