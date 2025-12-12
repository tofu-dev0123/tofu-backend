import math
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.schemas.post import Post as PostSchema, PostsPostRequest, PostsGetResponse
from app.models.post import Post as PostModel, PostStatus
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
    Postsテーブルから記事一覧を取得する
    """

    def get_posts(
        self,
        user_id: int,
        offset: int,
        limit: int,
        keyword: str | None,
        status: PostStatus | None,
    ):
        posts: List[PostSchema] = self.post_repo.find_posts_by_user(
            user_id,
            offset,
            limit,
            keyword,
            status
        )
        
        total_count = len(posts)
        total_pages = math.ceil(total_count / limit)
        posts_list = []
        
        for post in posts:
            posts_list.append(
                PostSchema(
                    post_id=post.post_id,
                    user_id=post.user_id,
                    title=post.title,
                    slug=post.slug,
                    thumbnail_url=post.thumbnail_url,
                    status=post.status,
                    publishedAt=post.published_at,
                    createdAt=post.created_at,
                    updatedAt=post.updated_at,
                )
            )
        
        return PostsGetResponse(
            total_count=total_count,
            total_pages=total_pages,
            posts=posts_list
        )

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

    def create_post(
        self, request: PostsPostRequest, id: int, slug: str, date: datetime
    ) -> int:
        post = PostModel(
            user_id=id,
            title=request.title,
            slug=slug,
            content_md=request.content_md,
            content_html=request.content_html,
            thumbnail_url=request.thumbnail_url,
            status=request.status,
            published_at=date,
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

    """
    記事の登録処理をする
    """

    def create_all(self, request: PostsPostRequest, user_id: int) -> int:
        try:
            # 画像IDの存在チェック
            if request.images:
                self.check_image_list(request.images)

            # タイトルからスラグを生成
            unique_slug = self.generate_slug_of_title(request.title)

            # タグからスラグを生成し登録するIDを取得
            tag_id_list = []
            if request.tags:
                tag_id_list.extend(self.generate_slug_of_tag_and_get_id(request.tags))

            # 公開ステータスの値をチェックして登録する日時を設定
            published_date = self.check_status_and_setting_date(request.status)

            # Postテーブルにインサートして新規記事IDを取得する
            new_post_id = self.create_post(
                request, user_id, unique_slug, published_date
            )

            # PostTagsの中間テーブルにIDを登録
            self.create_post_tag(tag_id_list, new_post_id)

            # Imageテーブルに記事IDを登録
            if request.images:
                self.attach_post_id_to_image(request.images, new_post_id)

            self.db.commit()

            return new_post_id

        except ImageNotExistError as e:
            raise e

        except:
            self.db.rollback()
            raise
