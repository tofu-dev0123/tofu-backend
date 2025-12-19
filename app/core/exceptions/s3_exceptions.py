from app.common.message import ErrorMessage


class S3FileUploadError(Exception):
    """S3アップロードエラー"""

    def __init__(self, message=ErrorMessage.S3_FILE_UPLOAD_ERROR):
        self.message = message
        super().__init__(self.message)
        

class S3FileDeleteError(Exception):
    """S3ファイル削除エラー"""

    def __init__(self, message=ErrorMessage.S3_FILE_UPLOAD_ERROR):
        self.message = message
        super().__init__(self.message)
