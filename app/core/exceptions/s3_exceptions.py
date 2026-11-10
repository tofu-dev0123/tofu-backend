from app.common.message import ErrorMessage
from app.core.exceptions.base import BaseAppError


class S3FileUploadError(BaseAppError):
    """S3アップロードエラー"""

    default_message = ErrorMessage.S3_FILE_UPLOAD_ERROR


class S3FileDeleteError(BaseAppError):
    """S3ファイル削除エラー"""

    default_message = ErrorMessage.S3_FILE_UPLOAD_ERROR
