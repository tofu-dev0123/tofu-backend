from sqlalchemy.orm import Session
from typing import List
from app.repositories.post_repository import PostRepository
from app.repositories.tag_repository import TagRepository
from app.repositories.image_repository import ImageRepository
from app.core.exceptions.post_exceptions import ImageNotExistError
from app.utils.slug_utils import generate_slug, increment_slug_suffix

class PostService:

    def __init__(self, db: Session):
        self.db = db
        self.post_repo = PostRepository(db)
        self.tag_repo = TagRepository(db)
        self.image_repo = ImageRepository(db)

    """
    画像IDがImageテーブルに登録されているをチェックする
    """
    def check_image_list(self, images: List[int]):
        for id in images:
            image_data = self.image_repo.find_by_image_id(self, id)

            if image_data is None:
                raise ImageNotExistError(message="")


    """
    タイトルからスラグを生成する
    """
    def generate_slug_of_title(self, title: str) -> str:
        # ベーススラグの生成
        base_slug = generate_slug(title)

        # DBから同一prefixのスラグ取得
        existing_slugs = self.post_repo.find_slugs_like(self, base_slug)
        
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
            id = self.tag_repo.find_id_by_name(self, tag_name)
            
            # DBからidを取得できたらそのidを使う
            if id is not None:
                slug_list.append(id)
                continue
            
            # ベーススラグの生成
            base_slug = generate_slug(tag_name)
            
            existing_slugs = self.tag_repo.find_slugs_starting_with(self,base_slug)
            
            # 同じものがなければそのまま返す
            if base_slug not in existing_slugs:
                return base_slug
            
            tag_slug = increment_slug_suffix(base_slug, existing_slugs)
            
            new_id = self.tag_repo.create(tag_name, tag_slug)
            
            slug_list.append(new_id)

        
        return slug_list