class ImageNotExistError(Exception):
    """画像IDが存在しないエラー"""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class ImageUploadValidationError(Exception):
    """画像アップロードバリデーションエラー"""

    def __init__(self, errors: list[dict]):
        self.errors = errors
        super().__init__("Image upload validation error")
