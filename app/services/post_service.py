from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.schemas.post import PostsPostRequest
from app.models.post import Post, PostStatus
from app.models.post_tag import PostTag
from app.repositories.post_repository import PostRepository
from app.repositories.tag_repository import TagRepository
from app.repositories.post_tag_repository import PostTagRepository
from app.repositories.image_repository import ImageRepository
from app.core.exceptions.post_exceptions import ImageNotExistError
from app.utils.slug_utils import generate_slug, increment_slug_suffix

class PostService:

    def __init__(self, db: Session):
        self.db = db
        self.post_repo = PostRepository(db)
        self.tag_repo = TagRepository(db)
        self.post_tag_repo = PostTagRepository(db)
        self.image_repo = ImageRepository(db)

    """
    画像IDがImageテーブルに登録されているをチェックする
    """
    def check_image_list(self, images: List[int]):
        for id in images:
            image_data = self.image_repo.find_by_image_id(id)

            if image_data is None:
                raise ImageNotExistError(message="")


    """
    タイトルからスラグを生成する
    """
    def generate_slug_of_title(self, title: str) -> str:
        # ベーススラグの生成
        base_slug = generate_slug(title)

        # DBから同一prefixのスラグ取得
        existing_slugs = self.post_repo.find_slugs_like(base_slug)
        
        # 同じものがなければそのまま返す
        if base_slug not in existing_slugs:
            return base_slug

        # 重複がある場合はインクリメントする
        title_slug = increment_slug_suffix(base_slug, existing_slugs)
        
        return title_slug

    """
    タグからスラグを生成してtag_idを取得する
    """
    def generate_slug_of_tag_and_get_id(self, tags: List[str]) -> List[int]:
        slug_list = []
        
        if not tags:
            return slug_list
        
        for tag_name in tags:
            id = self.tag_repo.find_id_by_name(tag_name)
            
            # DBからidを取得できたらそのidを使う
            if id:
                slug_list.append(id)
                continue
            
            # ベーススラグの生成
            base_slug = generate_slug(tag_name)
            
            existing_slugs = self.tag_repo.find_slugs_starting_with(base_slug)
            
            # 同じものがなければそのまま返す
            if base_slug not in existing_slugs:
                new_id = self.tag_repo.create(tag_name, base_slug)
                slug_list.append(new_id)
                continue
            
            tag_slug = increment_slug_suffix(base_slug, existing_slugs)
            
            new_id = self.tag_repo.create(tag_name, tag_slug)
            
            slug_list.append(new_id)

        return slug_list
    
    """
    公開ステータスの値をチェックして日時を返す
    """
    def check_status_and_setting_date(self, status: str) -> datetime | None:
        if status == PostStatus.PUBLISHED.value:
            return datetime.now()
        return None
    
    
    """
    Postテーブルに登録する  
    """
    def create_post(self, request: PostsPostRequest, id: int, slug: str, date: datetime) -> int:
        post = Post(
            user_id=id,
            title=request.title,
            slug=slug,
            content_md=request.content_md,
            content_html=request.content_html,
            thumbnail_url=request.thumbnail_url,
            status=request.status,
            published_at=date
        )
        
        post_id = self.post_repo.create(post)
        
        return post_id
    
    """
    PostTagテーブルに登録する  
    """
    def create_post_tag(self, tag_id_list: List[int], post_id: int):
        for id in tag_id_list:
            post_tag = PostTag(post_id=post_id, tag_id=id)
            self.post_tag_repo.create(post_tag)
    
    """
    画像テーブルに記事IDを登録する 
    """
    def attach_post_id_to_image(self, images: List[int], post_id: int):
        for id in images:
            self.image_repo.update_post_id(id, post_id)