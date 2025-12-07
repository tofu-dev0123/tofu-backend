from pydantic import BaseModel, Field, EmailStr


class LoginRequest(BaseModel):
    """ログインリクエストスキーマ"""

    username: EmailStr = Field(..., description="ユーザーネーム", max_length=50)
    password: str = Field(..., description="パスワード", min_length=8, max_length=50)


class LoginResponse(BaseModel):
    """ログイン成功レスポンススキーマ"""

    message: str = Field(..., description="メッセージ")
    token: str = Field(..., description="JWTトークン")


class LogoutResponse(BaseModel):
    """ログアウト成功レスポンススキーマ"""

    message: str = Field(..., description="メッセージ")
