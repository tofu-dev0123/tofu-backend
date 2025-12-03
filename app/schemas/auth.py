from pydantic import BaseModel, Field
from typing import List, Optional


class LoginRequest(BaseModel):
    """ログインリクエストスキーマ"""
    username: str = Field(..., description="ユーザーネーム")
    password: str = Field(..., description="パスワード")


class LoginResponse(BaseModel):
    """ログイン成功レスポンススキーマ"""
    message: str = Field(..., description="メッセージ")
    token: str = Field(..., description="JWTトークン")


class ErrorDetail(BaseModel):
    """エラー詳細スキーマ"""
    value: str = Field(..., description="項目")
    message: str = Field(..., description="メッセージ")


class ErrorResponse(BaseModel):
    """エラーレスポンススキーマ"""
    message: str = Field(..., description="メッセージ")
    error: str = Field(..., description="エラー")
    details: List[ErrorDetail] = Field(default_factory=list, description="詳細")

