from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError
from typing import List, Literal
from app.common.constant import Constant


class PostsPostRequest(BaseModel):
    """記事作成リクエストスキーマ"""

    title: str = Field(..., max_length=Constant.MAX_TITLE_LENGTH, description="タイトル")
    content_md: str = Field(..., description="マークダウン本文")
    content_html: str = Field(..., description="HTML本文")
    thumbnail_url: str | None = Field(
        None, max_length=Constant.MAX_THUMBNAIL_URL, description="サムネイル画像URL"
    )
    status: Literal["DRAFT", "PUBLISHED"] = Field(..., description="公開ステータス")
    images: List[int] = Field(default_factory=list, description="画像IDの配列")
    tags: List[str] = Field(default_factory=list, description="タグの配列")


    @field_validator("content_md")
    def validate_content_md_size(cls, v):
        if len(v.encode("utf-8")) > Constant.MAX_CONTENT_MARKDOWN_SIZE:
            raise PydanticCustomError("size_over", "")
        return v

    @field_validator("thumbnail_url")
    def empty_string_to_null(cls, v):
        return None if v == "" else v

    @field_validator("tags")
    def validate_tags(cls, v):
        if len(v) > Constant.MAX_TAGS:
            raise PydanticCustomError("list_too_long", "")

        for tag in v:
            if len(tag) > Constant.MAX_TAG_LENGTH:
                raise PydanticCustomError("string_too_long", "")

        return v


class PostsPostResponse(BaseModel):
    """記事作成成功レスポンススキーマ"""

    message: str = Field(..., description="メッセージ")
    post_id: int = Field(..., description="記事ID")
