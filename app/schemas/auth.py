from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """ログインリクエストスキーマ"""
    username: str = Field(..., description="ユーザーネーム")
    password: str = Field(..., description="パスワード")


class LoginResponse(BaseModel):
    """ログイン成功レスポンススキーマ"""
    message: str = Field(..., description="メッセージ")
    token: str = Field(..., description="JWTトークン")

