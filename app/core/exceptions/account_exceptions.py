from app.core.exceptions.base import BaseAppError


class PasswordMismatchError(BaseAppError):
    """パスワード不一致エラー"""


class EmailMismatchError(BaseAppError):
    """メールアドレス不一致エラー"""


class EmailAlreadyExistsError(BaseAppError):
    """メールアドレス重複エラー"""


class NewPasswordSameError(BaseAppError):
    """新しいパスワードが現在と同一のエラー"""
