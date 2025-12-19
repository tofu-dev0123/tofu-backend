from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """エラー詳細スキーマ"""

    value: str = Field(..., description="項目")
    message: str = Field(..., description="メッセージ")


class ErrorResponse(BaseModel):
    """エラーレスポンススキーマ"""

    message: str = Field(..., description="メッセージ")
    error: str = Field(..., description="エラー")
    details: list[ErrorDetail] = Field(default_factory=list, description="詳細")
