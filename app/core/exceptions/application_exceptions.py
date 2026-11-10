from app.core.exceptions.base import BaseAppError


class ApplicationError(BaseAppError):
    """汎用的なエラークラス"""

    def __init__(self, message: str, code: str) -> None:
        self.code = code
        super().__init__(message)
