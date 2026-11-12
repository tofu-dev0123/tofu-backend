from app.core.exceptions.base import BaseAppError


class SlugAlreadyExistsError(BaseAppError):
    """スラグ重複エラー"""
