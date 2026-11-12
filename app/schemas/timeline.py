from pydantic import BaseModel, Field, field_validator
from app.common.constant import Constant
from app.schemas.validators import max_length_validator


class Timeline(BaseModel):
    """年表エントリスキーマ"""

    timeline_id: int = Field(..., description="年表ID")
    year: int = Field(..., description="年")
    title: str | None = Field(None, description="見出し")
    body: str | None = Field(None, description="本文")
    sort_order: int = Field(..., description="表示順")


class TimelineListResponse(BaseModel):
    """年表一覧取得成功レスポンススキーマ"""

    timelines: list[Timeline] = Field(default_factory=list, description="年表一覧")


class _TimelineRequestBase(BaseModel):
    year: int = Field(
        ..., ge=Constant.MIN_YEAR, le=Constant.MAX_YEAR, description="年"
    )
    title: str | None = Field(None, description="見出し")
    body: str | None = Field(
        None, max_length=Constant.MAX_TIMELINE_BODY_LENGTH, description="本文"
    )
    sort_order: int = Field(0, ge=Constant.MIN_SORT_ORDER, description="表示順")

    _validate_title_length = field_validator("title")(
        max_length_validator(
            Constant.MAX_TIMELINE_TITLE_LENGTH, "timeline_title_too_long"
        )
    )


class TimelinePostRequest(_TimelineRequestBase):
    """年表作成リクエストスキーマ"""


class TimelinePutRequest(_TimelineRequestBase):
    """年表更新リクエストスキーマ"""


class TimelineResponse(BaseModel):
    """年表作成(更新)成功レスポンススキーマ"""

    message: str = Field(..., description="メッセージ")
    timeline_id: int = Field(..., description="年表ID")


class TimelineDeleteResponse(BaseModel):
    """年表削除成功レスポンススキーマ"""

    message: str = Field(..., description="メッセージ")
