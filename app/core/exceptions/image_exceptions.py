from app.common.message import ErrorMessage
from app.core.exceptions.base import BaseAppError


class ImageNotExistError(BaseAppError):
    """画像IDが存在しないエラー"""

    default_message = ErrorMessage.IMAGE_NOT_EXIST


class ImageUploadValidationError(Exception):
    """画像アップロードバリデーションエラー"""

    def __init__(self, errors: list[dict]) -> None:
        self.errors = errors
        super().__init__("Image upload validation error")


class ImageNotExistOnStorageError(BaseAppError):
    """画像がストレージに存在しないエラー"""

    default_message = ErrorMessage.NOT_EXIST_ON_STORAGE
