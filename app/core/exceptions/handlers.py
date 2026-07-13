import logging
from fastapi import Request
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.exceptions.auth_exceptions import LoginFailError, AuthenticationError
from app.core.exceptions.image_exceptions import (
    ImageNotExistError,
    ImageNotExistOnStorageError,
    ImageUploadValidationError,
)
from app.core.exceptions.s3_exceptions import S3FileUploadError
from app.core.exceptions.account_exceptions import (
    PasswordMismatchError,
    EmailMismatchError,
    EmailAlreadyExistsError,
)
from app.core.validation import VALIDATION_MESSAGES
from app.schemas.errors import ErrorResponse, ErrorDetail
from app.common.errorcode import ErrorCode
from app.common.message import ErrorMessage

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI):

    @app.exception_handler(ApplicationError)
    async def application_error_handler(request: Request, exc: ApplicationError):
        logger.warning(
            "application error",
            extra={"path": request.url.path, "code": exc.code},
        )
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                message=exc.message, error=exc.code, details=[]
            ).model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        errors = []

        for error in exc.errors():
            loc = error.get("loc")
            value = loc[1] if len(loc) > 1 else loc[0]
            type = error.get("type")

            msg = VALIDATION_MESSAGES.get((value, type)) or error.get("msg")
            errors.append({"value": str(value), "message": msg})

        logger.warning(
            "validation error",
            extra={"method": request.method, "path": request.url.path, "fields": [e["value"] for e in errors]},
        )

        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                message="", error=ErrorCode.VALIDATION_ERROR, details=errors
            ).model_dump(),
        )

    @app.exception_handler(LoginFailError)
    async def login_fail_handler(request: Request, exc: LoginFailError):
        logger.warning("login failed", extra={"path": request.url.path})
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                message=ErrorMessage.LOGIN_FAIL, error=ErrorCode.LOGIN_FAIL, details=[]
            ).model_dump(),
        )

    @app.exception_handler(HTTPException)
    async def no_token_handler(request, exc):
        if exc.status_code == 401 and exc.detail == "Not authenticated":
            return JSONResponse(
                status_code=401,
                content=ErrorResponse(
                    message=ErrorMessage.TOKEN_REQUIRED,
                    error=ErrorCode.AUTHENTICATION_ERROR,
                    details=[],
                ).model_dump(),
            )
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(AuthenticationError)
    async def authentication_error_handler(request: Request, exc: AuthenticationError):
        # メッセージが設定されている場合はそれを使用、そうでない場合はデフォルトメッセージ
        message = exc.message if exc.message else ErrorMessage.AUTHENTICATION_ERROR

        logger.warning("authentication error", extra={"path": request.url.path})

        return JSONResponse(
            status_code=401,
            content=ErrorResponse(
                message=message,
                error=ErrorCode.AUTHENTICATION_ERROR,
                details=[],
            ).model_dump(),
        )

    @app.exception_handler(ImageNotExistError)
    async def image_not_found_error_handler(request: Request, exc: ImageNotExistError):
        logger.warning("image not exist", extra={"path": request.url.path})
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                message=exc.message,
                error=ErrorCode.NOT_EXIST,
                details=[],
            ).model_dump(),
        )

    @app.exception_handler(ImageNotExistOnStorageError)
    async def not_exist_on_storage_error_handler(
        request: Request, exc: ImageNotExistOnStorageError
    ):
        logger.warning("image not exist on storage", extra={"path": request.url.path})
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                message=exc.message,
                error=ErrorCode.NOT_EXIST_ON_STORAGE,
                details=[],
            ).model_dump(),
        )

    @app.exception_handler(ImageUploadValidationError)
    async def image_upload_validation_error_handler(
        request: Request, exc: ImageUploadValidationError
    ):
        logger.warning("image upload validation error", extra={"path": request.url.path})

        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                message="", error=ErrorCode.VALIDATION_ERROR, details=[ErrorDetail(**e) for e in exc.errors]
            ).model_dump(),
        )

    @app.exception_handler(S3FileUploadError)
    async def s3_error_handler(request: Request, exc: S3FileUploadError):
        # S3 失敗の詳細は infra(s3.py) / service(image_service) 側で ERROR ログ済み
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                message=exc.message,
                error=ErrorCode.S3_ERROR,
                details=[],
            ).model_dump(),
        )

    @app.exception_handler(PasswordMismatchError)
    async def password_mismatch_error_handler(
        request: Request, exc: PasswordMismatchError
    ):
        logger.warning("password mismatch", extra={"path": request.url.path})
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                message=ErrorMessage.PASSWORD_MISMATCH,
                error=ErrorCode.PASSWORD_MISMATCH,
                details=[],
            ).model_dump(),
        )

    @app.exception_handler(EmailMismatchError)
    async def email_mismatch_error_handler(request: Request, exc: EmailMismatchError):
        logger.warning("email mismatch", extra={"path": request.url.path})
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                message=ErrorMessage.EMAIL_MISMATCH,
                error=ErrorCode.EMAIL_MISMATCH,
                details=[],
            ).model_dump(),
        )

    @app.exception_handler(EmailAlreadyExistsError)
    async def email_already_exists_error_handler(
        request: Request, exc: EmailAlreadyExistsError
    ):
        logger.warning("email already exists", extra={"path": request.url.path})
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                message=ErrorMessage.EMAIL_ALREADY_EXISTS,
                error=ErrorCode.EMAIL_ALREADY_EXISTS,
                details=[],
            ).model_dump(),
        )


class ApplicationError(Exception):
    """汎用的なエラークラス"""

    def __init__(self, message, code):
        self.message = message
        self.code = code
        super().__init__(self.message)
