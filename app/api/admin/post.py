from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.security import get_current_user
from app.core.exceptions.post_exceptions import ImageNotExistError
from app.common.message import Message
from app.schemas.post import PostsPostRequest, PostsPostResponse
from app.services.post_service import PostService
from app.models.user import User
from app.models.post import Post

router = APIRouter(prefix="/posts", tags=["Post 記事関連"])


@router.post("/", response_model=PostsPostResponse)
async def create_posts(
    request: PostsPostRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = PostService(db)
    
    try:
        # 画像IDの存在チェック
        if request.images:
            service.check_image_list(request.images)
            
        # タイトルからスラグを生成
        unique_slug = service.generate_slug_of_title(request.title)
        
        # タグからスラグを生成し登録するIDを取得
        tag_id_list = []
        if request.tags:
            tag_id_list.extend(service.generate_slug_of_tag_and_get_id(request.tags))
            
        # 公開ステータスの値をチェックして登録する日時を設定
        published_date = service.check_status_and_setting_date(request.status)
        
        # Postテーブルにインサートして新規記事IDを取得する
        new_post_id = service.create_post(request, current_user.user_id, unique_slug, published_date)
        
        # PostTagsの中間テーブルにIDを登録
        service.create_post_tag(tag_id_list, new_post_id)
        
        # Imageテーブルに記事IDを登録
        if request.images:
            service.attach_post_id_to_image(request.images, new_post_id)
        
        db.commit()

    except ImageNotExistError:
        raise
    
    except:
        db.rollback()
        raise
    

    return PostsPostResponse(message=Message.POST_CREATE_SUCCESS, post_id=new_post_id)