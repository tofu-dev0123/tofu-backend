import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from app.services.auth_service import login_service
from app.core.exceptions.auth_exceptions import LoginFailError


@pytest.fixture
def db():
    return Mock(spec=Session)


def test_login_success(db):
    mock_user = Mock()
    mock_user.user_id = 1
    mock_user.username = "testuser"
    mock_user.password = "hashed_password"

    with patch("app.services.auth_service.find_by_username", return_value=mock_user):
        with patch("app.services.auth_service.verify_password", return_value=True):
            with patch(
                "app.services.auth_service.create_access_token",
                return_value="fake_token",
            ) as mock_token:

                token = login_service("testuser", "correct_password", db)

                assert token == "fake_token"
                mock_token.assert_called_once_with(1, "testuser")


def test_login_user_not_found(db):
    with patch("app.services.auth_service.find_by_username", return_value=None):
        with pytest.raises(LoginFailError):
            login_service("unknown_user", "any_password", db)


def test_login_wrong_password(db):
    mock_user = Mock()
    mock_user.user_id = 1
    mock_user.username = "testuser"
    mock_user.password = "hashed_password"

    with patch("app.services.auth_service.find_by_username", return_value=mock_user):
        with patch("app.services.auth_service.verify_password", return_value=False):
            with pytest.raises(LoginFailError):
                login_service("testuser", "wrong_password", db)
