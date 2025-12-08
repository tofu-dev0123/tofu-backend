from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.security import get_current_user
from app.core.exceptions.post_exceptions import ImageNotExistError
from app.schemas.post import PostsPostRequest, PostsPostResponse
from app.services.post_service import check_image_list, generate_unique_slug

router = APIRouter(prefix="/posts", tags=["Post 記事関連"])


@router.post("/", response_model=PostsPostResponse)
async def create_posts(
    request: PostsPostRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        # 画像IDの存在チェック
        if len(request.images) > 0:
            check_image_list(request.images, db)
            
        # タイトルからスラグを生成
        unique_slug = generate_unique_slug(request.title, db)
        print(unique_slug)

    except ImageNotExistError:
        raise

    return PostsPostResponse(message="", post_id=0)
