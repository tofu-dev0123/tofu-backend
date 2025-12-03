from typing import List
from app.schemas.auth import LoginRequest, ErrorDetail


class ValidationError(Exception):
    """バリデーションエラー"""
    def __init__(self, message: str, details: List[ErrorDetail]):
        self.message = message
        self.details = details
        super().__init__(self.message)


def validate_login_request(request: LoginRequest) -> None:
    """
    ログインリクエストのバリデーションを行う
    
    Args:
        request: ログインリクエストオブジェクト
    
    Raises:
        ValidationError: バリデーションエラーがある場合
    """
    validation_errors = []
    
    if not request.username or not request.username.strip():
        validation_errors.append(
            ErrorDetail(value="username", message="ユーザー名は必須項目です")
        )
    
    if not request.password or not request.password.strip():
        validation_errors.append(
            ErrorDetail(value="password", message="パスワードは必須項目です")
        )
    
    if validation_errors:
        raise ValidationError(
            message="",
            details=validation_errors
        )

