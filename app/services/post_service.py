import math
from sqlalchemy.orm import Session
import logging
from datetime import datetime
from markdown_it import MarkdownIt
from app.schemas.post import (
    Post as PostSchema,
    PostsPostRequest,
    PostsPutRequest,
    PostsListGetResponse,
    PostGetResponse,
)
from botocore.exceptions import (
    ClientError,
    BotoCoreError,
)
from app.infra.storage.s3 import S3
from app.schemas.image import Image
from app.schemas.tag import Tag
from app.models.post import Post as PostModel, PostStatus
from app.models.post_tag import PostTag
from app.repositories.post_repository import PostRepository
from app.repositories.tag_repository import TagRepository
from app.repositories.post_tag_repository import PostTagRepository
from app.repositories.image_repository import ImageRepository
from app.repositories.queries.post_detail_query import PostDetailQueryRepository
from app.core.exceptions.image_exceptions import ImageNotExistError
from app.core.exceptions.s3_exceptions import S3FileDeleteError
from app.core.exceptions.handlers import ApplicationError
from app.common.errorcode import ErrorCode
from app.common.message import ErrorMessage
from app.utils.slug_utils import generate_slug, increment_slug_suffix


logger = logging.getLogger(__name__)


class PostService:

    def __init__(self, db: Session):
        self.db = db
        self.s3 = S3()
        self.post_repo = PostRepository(db)
        self.tag_repo = TagRepository(db)
        self.post_tag_repo = PostTagRepository(db)
        self.image_repo = ImageRepository(db)
        self.query_repo = PostDetailQueryRepository(db)
        self.md = MarkdownIt("gfm-like")

    """
    MarkdownからHTMLへの変換処理
    """

    def convert_markdown_to_html(self, markdown_text: str) -> str:
        html = self.md.render(markdown_text)
        return html

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
        posts: list[PostSchema] = self.post_repo.find_posts_by_user(
            user_id, offset, limit, keyword, status
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

        return PostsListGetResponse(
            total_count=total_count, total_pages=total_pages, posts=posts_list
        )

    """
    記事のサマリを取得する
    """

    def get_summary(self):
        summary = self.post_repo.get_post_counts()

        return summary

    """
    記事詳細を取得する
    """

    def get_post_detail(self, post_id: int) -> PostGetResponse:
        data = self.query_repo.find_by_post_id(post_id)
        images = []
        tags = []
        if data.images:
            images = [
                Image(
                    image_id=int(i[0]),
                    url=i[1],
                    alt_text=i[2],
                )
                for i in (img.split("|") for img in data.images.split(","))
            ]

        if data.tags:
            tags = [
                Tag(
                    tag_id=int(t[0]),
                    name=t[1],
                    slug=t[2],
                )
                for t in (tag.split("|") for tag in data.tags.split(","))
            ]

        result = PostGetResponse(
            post_id=post_id,
            title=data.title,
            slug=data.slug,
            content_md=data.content_md,
            content_html=data.content_html,
            thumbnail_url=data.thumbnail_url,
            status=data.status,
            images=images,
            tags=tags,
            published_at=data.published_at,
            created_at=data.created_at,
            updated_at=data.updated_at,
        )

        return result

    """
    画像IDがImageテーブルに登録されているをチェックする
    """

    def check_image_list(self, images: list[int]):
        for id in images:
            image_data = self.image_repo.find_by_image_id(id)

            if image_data is None:
                raise ImageNotExistError()

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

    def generate_slug_of_tag_and_get_id(self, tags: list[str]) -> list[int]:
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
        # MarkdownからHTMLへの変換
        content_html = self.convert_markdown_to_html(request.content_md)

        post = PostModel(
            user_id=id,
            title=request.title,
            slug=slug,
            content_md=request.content_md,
            content_html=content_html,
            thumbnail_url=request.thumbnail_url,
            status=request.status,
            published_at=date,
        )

        post_id = self.post_repo.create(post)

        return post_id

    """
    PostTagテーブルに登録する  
    """

    def create_post_tag(self, tag_id_list: list[int], post_id: int):
        for id in tag_id_list:
            post_tag = PostTag(post_id=post_id, tag_id=id)
            self.post_tag_repo.create(post_tag)

    """
    画像テーブルに記事IDを登録する 
    """

    def attach_post_id_to_image(self, images: list[int], post_id: int):
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

    """
    公開ステータスによって投稿日時を設定する
    """

    def set_published_at_from_status(
        self, post_id: int, new_status: PostStatus
    ) -> datetime | None:
        post = self.post_repo.find_by_post_id(post_id)

        old_status = post.status

        # DRAFT → PUBLISHED（初公開）
        if old_status == PostStatus.DRAFT and new_status == PostStatus.PUBLISHED:
            return datetime.now()

        # PUBLISHED → DRAFT（公開解除）
        if old_status == PostStatus.PUBLISHED and new_status == PostStatus.DRAFT:
            return None

        # PUBLISHED → PUBLISHED / DRAFT → DRAFT
        return post.published_at

    """
    画像の削除を行う
    """

    def delete_image_from_s3(self, url: str) -> None:
        try:
            object_key = self.s3.extract_key_from_url(url)
            self.s3.delete_object(object_key)
        except (ClientError, BotoCoreError):
            logger.exception("S3 delete failed")
            raise S3FileDeleteError()

    """
    サムネイルの更新処理を行う
    """

    def update_thumbnail(self, post_id: int, url: str | None, flag: bool) -> str | None:
        old_url = self.post_repo.find_thumbnail_url_by_post_id(post_id)

        # thumbnailDeleteFlag = true
        if flag:
            if url is not None:
                raise ApplicationError(
                    message=ErrorMessage.BAD_REQUEST_OF_THUMBNAIL,
                    code=ErrorCode.BAD_REQUEST_OF_THUMBNAIL,
                )

            if old_url:
                self.delete_image_from_s3(old_url)

            return None

        # flag = false & url 未指定 → 変更なし
        if url is None:
            return old_url

        # flag = false & 空文字 → 削除
        if url == "":
            if old_url:
                self.delete_image_from_s3(old_url)
            return None

        # flag = false & 差し替え
        if old_url and url != old_url:
            self.delete_image_from_s3(old_url)

        # 同一URL or 新規設定
        return url

    """
    画像の削除処理を行う
    """

    def extract_delete_images(self, post_id: int, images: list[int]):
        for id in images:
            image = self.image_repo.find_by_image_id(id)

            if not image:
                raise ImageNotExistError()

            if image.post_id != post_id:
                raise ApplicationError(
                    message=ErrorMessage.INVALID_IMAGE_OWNER.format(image_id=id),
                    code=ErrorCode.INVALID_IMAGE_OWNER,
                )

            self.delete_image_from_s3(image.url)

            self.image_repo.delete(id)

    """
    タグの更新処理をする
    """

    def update_tags(self, tags: list[str], post_id: int):
        # 新規タグIDリストを生成
        tag_id_list = self.generate_slug_of_tag_and_get_id(tags)

        # PostTagテーブルからpost_idに紐づく全レコードを削除
        self.post_tag_repo.delete_post_tags(post_id)

        # 生成したタグIDを再登録して更新
        self.create_post_tag(tag_id_list, post_id)

    """
    記事の更新処理をする
    """

    def update_all(self, request: PostsPutRequest, post_id: int):
        try:
            if not self.post_repo.exist_check_by_post_id(post_id):
                raise ApplicationError(
                    message=ErrorMessage.NOT_EXIST, code=ErrorCode.NOT_EXIST
                )

            # ステータスの値によって投稿日時をセット
            new_published_at = self.set_published_at_from_status(
                post_id, request.status
            )

            # 更新するサムネイルURLをセット
            update_url = self.update_thumbnail(
                post_id, request.thumbnail_url, request.thumbnail_delete_flag
            )

            # 削除する画像の処理
            if request.delete_images:
                self.extract_delete_images(post_id, request.delete_images)

            # タグの更新処理
            if request.tags:
                self.update_tags(request.tags, post_id)

            # MarkdownからHTMLへの変換
            content_html = self.convert_markdown_to_html(request.content_md)

            # 更新処理
            self.post_repo.update_post(
                post_id=post_id,
                title=request.title,
                content_md=request.content_md,
                content_html=content_html,
                status=request.status,
                published_at=new_published_at,
                thumbnail_url=update_url,
            )

            # 新規登録画像に記事IDを登録
            if request.new_images:
                self.attach_post_id_to_image(request.new_images, post_id)

            self.db.commit()

        except:
            self.db.rollback()
            raise

        return

    """
    サムネイルの削除処理をする
    """

    def delete_thumbnail(self, post_id: int):
        thumbnail = self.post_repo.find_thumbnail_url_by_post_id(post_id)

        if thumbnail:
            self.delete_image_from_s3(thumbnail)

    """
    記事IDを参照して画像の削除処理をする
    """

    def delete_image_from_post_id(self, post_id: int):
        image_urls = self.image_repo.find_url_by_post_id(post_id)

        for url in image_urls:
            self.delete_image_from_s3(url)

    """
    記事の削除処理をする
    """

    def delete_all(self, post_id: int):
        try:
            if not self.post_repo.exist_check_by_post_id(post_id):
                raise ApplicationError(
                    message=ErrorMessage.NOT_EXIST, code=ErrorCode.NOT_EXIST
                )

            #  サムネイルの削除処理
            self.delete_thumbnail(post_id)

            # 記事とタグの中間テーブルの削除処理
            self.post_tag_repo.delete_post_tags(post_id)

            # 登録されている画像の削除処理
            self.delete_image_from_post_id(post_id)

            # 画像レコードの削除処理
            self.image_repo.delete_from_post_id(post_id)

            # 記事レコードの削除
            self.post_repo.delete(post_id)

            self.db.commit()

        except:
            self.db.rollback()
            raise

    def patch_status(self, status: PostStatus, post_id: int):
        try:
            # 公開ステータスの値によって投稿日時を更新
            published_at = self.set_published_at_from_status(post_id, status)

            self.post_repo.update_status_and_published_at(post_id, status, published_at)

            self.db.commit()
        except:
            self.db.rollback()
            raise
