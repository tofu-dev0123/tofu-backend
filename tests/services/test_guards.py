import pytest
from app.services.guards import ensure_exists
from app.core.exceptions.application_exceptions import ApplicationError
from app.common.errorcode import ErrorCode
from app.common.message import ErrorMessage


# 値が存在する場合はそのまま返す
def test_ensure_exists_returns_value():
    value = object()

    assert ensure_exists(value) is value


# 存在チェック結果が True の場合は True を返す
def test_ensure_exists_true():
    assert ensure_exists(True) is True


# None の場合は既定メッセージで NOT_EXIST を送出する
def test_ensure_exists_none_raises():
    with pytest.raises(ApplicationError) as exc_info:
        ensure_exists(None)

    assert exc_info.value.code == ErrorCode.NOT_EXIST
    assert exc_info.value.message == ErrorMessage.NOT_EXIST


# False の場合は指定メッセージで NOT_EXIST を送出する
def test_ensure_exists_false_raises_with_message():
    with pytest.raises(ApplicationError) as exc_info:
        ensure_exists(False, ErrorMessage.PRODUCT_NOT_EXIST)

    assert exc_info.value.code == ErrorCode.NOT_EXIST
    assert exc_info.value.message == ErrorMessage.PRODUCT_NOT_EXIST
