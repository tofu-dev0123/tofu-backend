import pytest
from unittest.mock import MagicMock
from app.services.transaction import transaction


# 正常終了時は commit のみ呼ばれる
def test_transaction_success_commit():
    mock_db = MagicMock()

    with transaction(mock_db):
        pass

    mock_db.commit.assert_called_once()
    mock_db.rollback.assert_not_called()


# 例外発生時は rollback して再送出し、commit は呼ばれない
def test_transaction_exception_rollback():
    mock_db = MagicMock()

    with pytest.raises(ValueError):
        with transaction(mock_db):
            raise ValueError("error")

    mock_db.rollback.assert_called_once()
    mock_db.commit.assert_not_called()
