from app.common.message import ErrorMessage


class S3FileUploadError(Exception):
    """画像IDが存在しないエラー"""

    def __init__(self, message=ErrorMessage.S3_FILE_UPLOAD_ERROR):
        self.message = message
        super().__init__(self.message)
