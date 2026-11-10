from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_core import PydanticCustomError
from typing import Any, Self
from datetime import datetime
from app.common.constant import Constant
from app.models.post import PostStatus
from app.schemas.tag import Tag
from app.schemas.image import Image
from app.schemas.validators import (
    empty_string_to_none,
    validate_content_md_size,
    validate_tags,
)


class Post(BaseModel):
    post_id: int = Field(..., description="記事ID")
    user_id: int = Field(..., description="ユーザーID")
    title: str | None = Field(None, description="タイトル")
    slug: str = Field(..., description="スラグ")
    thumbnail_url: str | None = Field(None, description="サムネイルURL")
    status: PostStatus = Field(..., description="公開ステータス")
    publishedAt: datetime | None = Field(None, description="投稿日時")
    createdAt: datetime = Field(..., description="作成日時")
    updatedAt: datetime = Field(..., description="更新日時")


class PostPublishAt(BaseModel):
    post_id: int = Field(..., description="記事ID")
    title: str | None = Field(None, description="タイトル")
    slug: str = Field(..., description="スラグ")
    thumbnail_url: str | None = Field(None, description="サムネイルURL")
    published_at: datetime | None = Field(None, description="公開日時")
    tags: list[Tag] = Field(default_factory=list, description="タグデータの配列")


class PostsListGetResponse(BaseModel):
    """記事一覧取得成功レスポンススキーマ"""

    total_count: int = Field(..., description="総件数")
    total_pages: int = Field(..., description="総ページ数")
    posts: list[Post] = Field(default_factory=list, description="記事一覧")


class PostsSummaryResponse(BaseModel):
    """記事件数取得成功レスポンススキーマ"""

    total_count: int = Field(..., description="総件数")
    published_count: int = Field(..., description="公開済件数")
    draft_count: int = Field(..., description="下書き件数")


class PostGetResponse(BaseModel):
    """記事取得成功レスポンススキーマ"""

    post_id: int = Field(..., description="記事ID")
    title: str | None = Field(None, description="タイトル")
    slug: str = Field(..., description="スラグ")
    content_md: str = Field(..., description="マークダウン本文")
    content_html: str = Field(..., description="HTML本文")
    thumbnail_id: int | None = Field(None, description="サムネイル画像ID")
    thumbnail_url: str | None = Field(None, description="サムネイル画像URL")
    thumbnail_alt_text: str | None = Field(
        None, description="サムネイル画像代替テキスト"
    )
    status: PostStatus = Field(..., description="公開ステータス")
    images: list[Image] = Field(default_factory=list, description="画像データの配列")
    tags: list[Tag] = Field(default_factory=list, description="タグデータの配列")
    published_at: datetime | None = Field(None, description="公開日時")
    created_at: datetime = Field(..., description="記事作成日時")
    updated_at: datetime = Field(..., description="記事更新日時")


class PostsPostRequest(BaseModel):
    """記事作成リクエストスキーマ"""

    title: str | None = Field(
        None, max_length=Constant.MAX_TITLE_LENGTH, description="タイトル"
    )
    content_md: str = Field(..., description="マークダウン本文")
    thumbnail_url: str | None = Field(
        None, max_length=Constant.MAX_THUMBNAIL_URL, description="サムネイル画像URL"
    )
    status: PostStatus = Field(..., description="公開ステータス")
    images: list[int] = Field(default_factory=list, description="画像IDの配列")
    tags: list[str] = Field(default_factory=list, description="タグの配列")

    @field_validator("title", mode="before")
    @classmethod
    def empty_title_to_none(cls, v: Any) -> Any:
        """空文字列を None に変換（DRAFT でのタイトル未入力を許容）"""
        return None if v == "" else v

    _validate_content_md_size = field_validator("content_md")(validate_content_md_size)
    _empty_string_to_none = field_validator("thumbnail_url")(empty_string_to_none)
    _validate_tags = field_validator("tags")(validate_tags)

    @model_validator(mode="after")
    def validate_title_for_published(self) -> Self:
        """PUBLISHED 時はタイトルを必須とする"""
        if self.status == PostStatus.PUBLISHED and not self.title:
            raise PydanticCustomError("title_required_for_published", "")
        return self


class PostsPutRequest(BaseModel):
    """記事更新リクエストスキーマ"""

    title: str = Field(
        ..., max_length=Constant.MAX_TITLE_LENGTH, description="タイトル"
    )
    content_md: str = Field(..., description="マークダウン本文")
    thumbnail_url: str | None = Field(
        None, max_length=Constant.MAX_THUMBNAIL_URL, description="サムネイル画像URL"
    )
    thumbnail_delete_flag: bool = Field(..., description="サムネイル削除フラグ")
    status: PostStatus = Field(..., description="公開ステータス")
    delete_images: list[int] = Field(
        default_factory=list, description="削除対象の画像IDの配列"
    )
    new_images: list[int] = Field(
        default_factory=list, description="新規登録対象の画像IDの配列"
    )
    tags: list[str] = Field(default_factory=list, description="タグの配列")

    _validate_content_md_size = field_validator("content_md")(validate_content_md_size)
    _empty_string_to_none = field_validator("thumbnail_url")(empty_string_to_none)
    _validate_tags = field_validator("tags")(validate_tags)


class PostsResponse(BaseModel):
    """記事作成(更新)成功レスポンススキーマ"""

    message: str = Field(..., description="メッセージ")
    post_id: int = Field(..., description="記事ID")


class PostsDeleteResponse(BaseModel):
    """記事作成(更新)成功レスポンススキーマ"""

    message: str = Field(..., description="メッセージ")


class PostsPatchRequest(BaseModel):
    """公開ステータス更新リクエストスキーマ"""

    status: PostStatus = Field(..., description="公開ステータス")


class PostsPatchResponse(BaseModel):
    """公開ステータス更新成功レスポンススキーマ"""

    message: str = Field(..., description="メッセージ")


class PostsPublishAtResponse(BaseModel):
    """公開記事取得成功レスポンススキーマ"""

    total_count: int = Field(..., description="総件数")
    total_pages: int = Field(..., description="総ページ数")
    page: int = Field(..., description="ページ")
    limit: int = Field(..., description="リミット")
    posts: list[PostPublishAt] = Field(default_factory=list, description="記事一覧")


class PostSlugsResponse(BaseModel):
    """公開記事スラグ一覧取得成功レスポンススキーマ"""

    slugs: list[str] = Field(default_factory=list, description="公開記事のスラグ配列")


class PostPublishAtResponse(BaseModel):
    """公開記事取得成功レスポンススキーマ"""

    post_id: int = Field(..., description="記事ID")
    title: str = Field(..., description="タイトル")
    slug: str = Field(..., description="スラグ")
    content_html: str = Field(..., description="HTML本文")
    thumbnail_url: str | None = Field(None, description="サムネイルURL")
    tags: list[Tag] = Field(default_factory=list, description="タグ一覧")
    published_at: datetime = Field(..., description="公開日時")
