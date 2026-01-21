from pydantic import BaseModel, Field, EmailStr, field_validator
from app.common.constant import Constant


class UpdateAccountNameRequest(BaseModel):
    """アカウント名変更リクエストスキーマ"""

    account_name: str = Field(
        ...,
        description="アカウント名",
        min_length=1,
        max_length=Constant.MAX_ACCOUNT_NAME_LENGTH,
    )

    @field_validator("account_name")
    @classmethod
    def validate_not_blank(cls, v: str) -> str:
        if v.strip() == "":
            raise ValueError("空白のみは不可です")
        return v


class UpdateAccountNameResponse(BaseModel):
    """アカウント名変更成功レスポンススキーマ"""

    message: str = Field(..., description="メッセージ")
    user_id: int = Field(..., description="ユーザーID")
    account_name: str = Field(..., description="アカウント名")


class ChangePasswordRequest(BaseModel):
    """パスワード変更リクエストスキーマ"""

    current_password: str = Field(
        ...,
        description="現在のパスワード",
        min_length=Constant.MIN_PASSWORD_LENGTH,
        max_length=Constant.MAX_PASSWORD_LENGTH,
    )
    new_password: str = Field(
        ...,
        description="新しいパスワード",
        min_length=Constant.MIN_PASSWORD_LENGTH,
        max_length=Constant.MAX_PASSWORD_LENGTH,
    )


class ChangePasswordResponse(BaseModel):
    """パスワード変更成功レスポンススキーマ"""

    message: str = Field(..., description="メッセージ")


class ChangeEmailRequest(BaseModel):
    """メールアドレス変更リクエストスキーマ"""

    current_email: EmailStr = Field(
        ...,
        description="現在のメールアドレス",
        max_length=Constant.MAX_USERNAME_LENGTH,
    )
    new_email: EmailStr = Field(
        ...,
        description="新しいメールアドレス",
        max_length=Constant.MAX_USERNAME_LENGTH,
    )
    password: str = Field(
        ...,
        description="現在のパスワード",
        min_length=Constant.MIN_PASSWORD_LENGTH,
        max_length=Constant.MAX_PASSWORD_LENGTH,
    )


class ChangeEmailResponse(BaseModel):
    """メールアドレス変更成功レスポンススキーマ"""

    message: str = Field(..., description="メッセージ")
    user_id: int = Field(..., description="ユーザーID")
    username: str = Field(..., description="メールアドレス")
