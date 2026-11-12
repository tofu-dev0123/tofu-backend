import calendar
import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock, patch
from jose import jwt
from app.core.config import settings
from app.core.security import (
    create_access_token,
    verify_token,
    hash_password,
    verify_password,
    get_current_user,
)
from app.core.exceptions.auth_exceptions import AuthenticationError
from app.common.message import ErrorMessage


def _request(cookies: dict | None = None, headers: dict | None = None) -> Mock:
    request = Mock()
    request.cookies = cookies or {}
    request.headers = headers or {}
    return request


# ==================== トークン ====================


# 作成したトークンを検証するとペイロードが取り出せる
def test_create_and_verify_token():
    token = create_access_token(user_id=1, username="test@example.com")

    payload = verify_token(token)

    assert payload["sub"] == "1"
    assert payload["username"] == "test@example.com"


# 有効期限は注入した現在時刻 + 3 時間
def test_create_access_token_expire_from_now():
    now = datetime.utcnow().replace(microsecond=0)

    token = create_access_token(user_id=1, username="u", now=now)

    payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
        options={"verify_exp": False},
    )
    # jose は naive datetime を UTC として epoch 秒に変換する
    assert payload["exp"] == calendar.timegm((now + timedelta(hours=3)).utctimetuple())


# 期限切れトークンは AuthenticationError
def test_verify_token_expired():
    token = create_access_token(
        user_id=1, username="u", now=datetime.utcnow() - timedelta(hours=4)
    )

    with pytest.raises(AuthenticationError):
        verify_token(token)


# 改ざん・不正なトークンは AuthenticationError
def test_verify_token_invalid():
    with pytest.raises(AuthenticationError):
        verify_token("invalid-token")


# ==================== パスワード ====================


def test_hash_and_verify_password():
    hashed = hash_password("password")

    assert hashed != "password"
    assert verify_password("password", hashed) is True
    assert verify_password("wrong", hashed) is False


# ==================== get_current_user ====================


# Authorization ヘッダのトークンからユーザーを取得する
@patch("app.core.security.UserRepository")
def test_get_current_user_from_header(mock_repo_cls):
    user = Mock()
    mock_repo_cls.return_value.find_by_id.return_value = user
    token = create_access_token(user_id=5, username="u")
    db = MagicMock()

    result = get_current_user(_request(headers={"Authorization": f"Bearer {token}"}), db)

    assert result is user
    mock_repo_cls.assert_called_once_with(db)
    mock_repo_cls.return_value.find_by_id.assert_called_once_with(5)


# クッキーのトークンを優先して使う
@patch("app.core.security.UserRepository")
def test_get_current_user_from_cookie(mock_repo_cls):
    user = Mock()
    mock_repo_cls.return_value.find_by_id.return_value = user
    token = create_access_token(user_id=7, username="u")

    result = get_current_user(_request(cookies={"auth_token": token}), MagicMock())

    assert result is user
    mock_repo_cls.return_value.find_by_id.assert_called_once_with(7)


# トークンがない場合は TOKEN_REQUIRED
def test_get_current_user_no_token():
    with pytest.raises(AuthenticationError) as exc_info:
        get_current_user(_request(), MagicMock())

    assert exc_info.value.message == ErrorMessage.TOKEN_REQUIRED


# Bearer 以外の Authorization ヘッダはトークンなし扱い
def test_get_current_user_not_bearer():
    with pytest.raises(AuthenticationError) as exc_info:
        get_current_user(_request(headers={"Authorization": "Basic xxx"}), MagicMock())

    assert exc_info.value.message == ErrorMessage.TOKEN_REQUIRED


# ユーザーが存在しない場合は AuthenticationError
@patch("app.core.security.UserRepository")
def test_get_current_user_user_not_found(mock_repo_cls):
    mock_repo_cls.return_value.find_by_id.return_value = None
    token = create_access_token(user_id=99, username="u")

    with pytest.raises(AuthenticationError):
        get_current_user(_request(headers={"Authorization": f"Bearer {token}"}), MagicMock())
