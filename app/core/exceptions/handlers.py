import logging
from collections.abc import Awaitable, Callable
from typing import Any
from fastapi import Request
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.exceptions.application_exceptions import ApplicationError
from app.core.exceptions.base import BaseAppError
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


def _error_response(
    status_code: int,
    message: str,
    error: str,
    details: list[Any] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(
            message=message, error=error, details=details or []
        ).model_dump(),
    )


def _fixed(message: str) -> Callable[[BaseAppError], str]:
    """例外の内容によらず固定のメッセージを返す"""
    return lambda exc: message


def _from_exc(exc: BaseAppError) -> str:
    """例外に設定されたメッセージを返す"""
    return exc.message


def _from_exc_or(default: str) -> Callable[[BaseAppError], str]:
    """例外にメッセージが設定されていればそれを、なければ default を返す"""
    return lambda exc: exc.message or default


# (例外クラス, ステータス, エラーコード, メッセージの取り方, WARNING ログ文言 or None)
# S3FileUploadError は infra/service 側で ERROR ログ済みのため再ログしない
_SIMPLE_HANDLERS: list[
    tuple[type[BaseAppError], int, str, Callable[[BaseAppError], str], str | None]
] = [
    (LoginFailError, 400, ErrorCode.LOGIN_FAIL, _fixed(ErrorMessage.LOGIN_FAIL), "login failed"),
    (
        AuthenticationError,
        401,
        ErrorCode.AUTHENTICATION_ERROR,
        _from_exc_or(ErrorMessage.AUTHENTICATION_ERROR),
        "authentication error",
    ),
    (ImageNotExistError, 400, ErrorCode.NOT_EXIST, _from_exc, "image not exist"),
    (
        ImageNotExistOnStorageError,
        400,
        ErrorCode.NOT_EXIST_ON_STORAGE,
        _from_exc,
        "image not exist on storage",
    ),
    (S3FileUploadError, 400, ErrorCode.S3_ERROR, _from_exc, None),
    (
        PasswordMismatchError,
        400,
        ErrorCode.PASSWORD_MISMATCH,
        _fixed(ErrorMessage.PASSWORD_MISMATCH),
        "password mismatch",
    ),
    (
        EmailMismatchError,
        400,
        ErrorCode.EMAIL_MISMATCH,
        _fixed(ErrorMessage.EMAIL_MISMATCH),
        "email mismatch",
    ),
    (
        EmailAlreadyExistsError,
        400,
        ErrorCode.EMAIL_ALREADY_EXISTS,
        _fixed(ErrorMessage.EMAIL_ALREADY_EXISTS),
        "email already exists",
    ),
]


def _make_simple_handler(
    status_code: int,
    error: str,
    get_message: Callable[[BaseAppError], str],
    log_message: str | None,
) -> Callable[[Request, Exception], Awaitable[JSONResponse]]:
    async def handler(request: Request, exc: Exception) -> JSONResponse:
        assert isinstance(exc, BaseAppError)
        if log_message is not None:
            logger.warning(log_message, extra={"path": request.url.path})
        return _error_response(status_code, get_message(exc), error)

    return handler


def register_exception_handlers(app: FastAPI):

    for exc_class, status_code, error, get_message, log_message in _SIMPLE_HANDLERS:
        app.add_exception_handler(
            exc_class,
            _make_simple_handler(status_code, error, get_message, log_message),
        )

    @app.exception_handler(ApplicationError)
    async def application_error_handler(request: Request, exc: ApplicationError):
        logger.warning(
            "application error",
            extra={"path": request.url.path, "code": exc.code},
        )
        return _error_response(400, exc.message, exc.code)

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

        return _error_response(400, "", ErrorCode.VALIDATION_ERROR, errors)

    @app.exception_handler(HTTPException)
    async def no_token_handler(request, exc):
        if exc.status_code == 401 and exc.detail == "Not authenticated":
            return _error_response(
                401, ErrorMessage.TOKEN_REQUIRED, ErrorCode.AUTHENTICATION_ERROR
            )
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(ImageUploadValidationError)
    async def image_upload_validation_error_handler(
        request: Request, exc: ImageUploadValidationError
    ):
        logger.warning("image upload validation error", extra={"path": request.url.path})

        return _error_response(
            400, "", ErrorCode.VALIDATION_ERROR, [ErrorDetail(**e) for e in exc.errors]
        )
