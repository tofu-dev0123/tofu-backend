from fastapi import Request
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.exceptions.auth_exceptions import LoginFailError, AuthenticationError
from app.core.exceptions.post_exceptions import ImageNotExistError
from app.core.validation import VALIDATION_MESSAGES
from app.schemas.errors import ErrorResponse
from app.common.errorcode import ErrorCode
from app.common.message import ErrorMessage


def register_exception_handlers(app: FastAPI):

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        errors = []

        for error in exc.errors():
            value = error.get("loc")[1]
            type = error.get("type")
            print(error.get("loc"))
            print(type)

            msg = VALIDATION_MESSAGES.get((value, type)) or error.get("msg")
            errors.append({"value": str(value), "message": msg})

        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                message="", error=ErrorCode.VALIDATION_ERROR, details=errors
            ).dict(),
        )

    @app.exception_handler(LoginFailError)
    async def login_fail_handler(request: Request, exc: LoginFailError):
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                message=ErrorMessage.LOGIN_FAIL, error=ErrorCode.LOGIN_FAIL, details=[]
            ).dict(),
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
                ).dict(),
            )
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(AuthenticationError)
    async def authentication_error_handler(request: Request, exc: AuthenticationError):
        return JSONResponse(
            status_code=401,
            content=ErrorResponse(
                message=ErrorMessage.AUTHENTICATION_ERROR,
                error=ErrorCode.AUTHENTICATION_ERROR,
                details=[],
            ).dict(),
        )

    @app.exception_handler(ImageNotExistError)
    async def image_not_found_error_handler(request: Request, exc: AuthenticationError):
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                message=ErrorMessage.IMAGE_NOT_EXIST,
                error=ErrorCode.NOT_EXIST,
                details=[],
            ).dict(),
        )
