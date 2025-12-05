from fastapi import Request
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.validation import VALIDATION_MESSAGES
from app.schemas.errors import ErrorResponse
from app.core.message import ErrorMessage
from app.core.errorcode import ErrorCode

def register_exception_handlers(app: FastAPI):

  @app.exception_handler(RequestValidationError)
  async def validation_error_handler(request: Request, exc: RequestValidationError):
    errors = []

    for error in exc.errors():
      value = error.get("loc")[-1]
      type = error.get("type")
      print(value)
      print(type)

      msg = VALIDATION_MESSAGES.get((value, type)) or error.get("msg")
      errors.append({
        "value": str(value),
        "message": msg
      })
      
    return JSONResponse(
      status_code=400,
      content=ErrorResponse(
        message="",
        error=ErrorCode.VALIDATION_ERROR,
        details=errors
      ).dict()
    )

