from pydantic import BaseModel, Field
from app.common.constant import Constant
from app.schemas.timeline import Timeline


class ProfileResponse(BaseModel):
    """プロフィール取得成功レスポンススキーマ"""

    headline: str = Field(..., description="肩書き")
    bio: str = Field(..., description="自己紹介文")
    site_description: str = Field(..., description="サイト説明文")


class ProfilePutRequest(BaseModel):
    """プロフィール更新リクエストスキーマ"""

    headline: str = Field(
        ..., max_length=Constant.MAX_HEADLINE_LENGTH, description="肩書き"
    )
    bio: str = Field(..., max_length=Constant.MAX_BIO_LENGTH, description="自己紹介文")
    site_description: str = Field(
        ..., max_length=Constant.MAX_SITE_DESCRIPTION_LENGTH, description="サイト説明文"
    )


class ProfilePutResponse(BaseModel):
    """プロフィール更新成功レスポンススキーマ"""

    message: str = Field(..., description="メッセージ")


class AboutResponse(BaseModel):
    """公開 About ページ取得成功レスポンススキーマ"""

    profile: ProfileResponse = Field(..., description="プロフィール")
    timelines: list[Timeline] = Field(default_factory=list, description="年表一覧")
