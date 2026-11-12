from typing import TypeVar
from app.core.exceptions.application_exceptions import ApplicationError
from app.common.errorcode import ErrorCode
from app.common.message import ErrorMessage

T = TypeVar("T")


def ensure_exists(value: T | None, message: str = ErrorMessage.NOT_EXIST) -> T:
    """値が存在しない（None / False 等の偽）場合は NOT_EXIST を送出し、存在すれば値を返す"""
    if not value:
        raise ApplicationError(message=message, code=ErrorCode.NOT_EXIST)
    return value
