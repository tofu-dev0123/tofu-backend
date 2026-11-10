from pydantic import BaseModel, Field, field_validator
from app.common.constant import Constant
from app.schemas.tag import Tag
from app.schemas.validators import (
    empty_string_to_none,
    max_length_validator,
    validate_tags,
)


class Product(BaseModel):
    """プロダクトエントリスキーマ"""

    product_id: int = Field(..., description="プロダクトID")
    title: str = Field(..., description="タイトル")
    description: str | None = Field(None, description="説明")
    link_url: str | None = Field(None, description="リンクURL")
    github_url: str | None = Field(None, description="GitHubリンクURL")
    published: bool = Field(..., description="公開フラグ")
    sort_order: int = Field(..., description="表示順")
    tags: list[Tag] = Field(default_factory=list, description="技術タグの配列")


class ProductListResponse(BaseModel):
    """プロダクト一覧取得成功レスポンススキーマ"""

    products: list[Product] = Field(default_factory=list, description="プロダクト一覧")


class _ProductRequestBase(BaseModel):
    title: str = Field(..., description="タイトル")
    description: str | None = Field(
        None, max_length=Constant.MAX_PRODUCT_DESCRIPTION_LENGTH, description="説明"
    )
    link_url: str | None = Field(
        None, max_length=Constant.MAX_LINK_URL_LENGTH, description="リンクURL"
    )
    github_url: str | None = Field(
        None, max_length=Constant.MAX_LINK_URL_LENGTH, description="GitHubリンクURL"
    )
    published: bool = Field(False, description="公開フラグ")
    sort_order: int = Field(0, ge=Constant.MIN_SORT_ORDER, description="表示順")
    tags: list[str] = Field(default_factory=list, description="技術タグの配列")

    _empty_string_to_none = field_validator("description", "link_url", "github_url")(
        empty_string_to_none
    )
    _validate_tags = field_validator("tags")(validate_tags)
    _validate_title_length = field_validator("title")(
        max_length_validator(Constant.MAX_PRODUCT_TITLE_LENGTH, "product_title_too_long")
    )


class ProductPostRequest(_ProductRequestBase):
    """プロダクト作成リクエストスキーマ"""


class ProductPutRequest(_ProductRequestBase):
    """プロダクト更新リクエストスキーマ"""


class ProductResponse(BaseModel):
    """プロダクト作成(更新)成功レスポンススキーマ"""

    message: str = Field(..., description="メッセージ")
    product_id: int = Field(..., description="プロダクトID")


class ProductDeleteResponse(BaseModel):
    """プロダクト削除成功レスポンススキーマ"""

    message: str = Field(..., description="メッセージ")
