from app.core.exceptions.base import BaseAppError


class LoginFailError(BaseAppError):
    """ログイン失敗エラー"""


class AuthenticationError(BaseAppError):
    """認証エラー"""
