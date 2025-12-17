from app.common.message import ErrorMessage


class ImageNotExistError(Exception):
    """画像IDが存在しないエラー"""

    def __init__(self, message=ErrorMessage.IMAGE_NOT_EXIST):
        self.message = message
        super().__init__(self.message)


class ImageUploadValidationError(Exception):
    """画像アップロードバリデーションエラー"""

    def __init__(self, errors: list[dict]):
        self.errors = errors
        super().__init__("Image upload validation error")


class ImageNotExistOnStorageError(Exception):
    """画像がストレージに存在しないエラー"""

    def __init__(self, message=ErrorMessage.NOT_EXIST_ON_STORAGE):
        self.message = message
        super().__init__(self.message)
