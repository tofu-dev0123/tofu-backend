import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from app.services.auth_service import AuthService
from app.core.exceptions.auth_exceptions import LoginFailError


@pytest.fixture
def db():
    return Mock(spec=Session)


def test_login_success(db):
    mock_user = Mock()
    mock_user.user_id = 1
    mock_user.username = "testuser"
    mock_user.password = "hashed_password"

    with patch("app.repositories.user_repository.UserRepository.find_by_username", return_value=mock_user):
        with patch("app.services.auth_service.verify_password", return_value=True):
            with patch(
                "app.services.auth_service.create_access_token",
                return_value="fake_token",
            ) as mock_token:
                
                service = AuthService(db)
                token = service.login("testuser", "correct_password")

                assert token == "fake_token"
                mock_token.assert_called_once_with(1, "testuser")


def test_login_user_not_found(db):
    with patch("app.repositories.user_repository.UserRepository.find_by_username", return_value=None):
        with pytest.raises(LoginFailError):
            service = AuthService(db)
            service.login("unknown_user", "any_password")


def test_login_wrong_password(db):
    mock_user = Mock()
    mock_user.user_id = 1
    mock_user.username = "testuser"
    mock_user.password = "hashed_password"

    with patch("app.repositories.user_repository.UserRepository.find_by_username", return_value=mock_user):
        with patch("app.services.auth_service.verify_password", return_value=False):
            with pytest.raises(LoginFailError):
                service = AuthService(db)
                service.login("testuser", "wrong_password")
