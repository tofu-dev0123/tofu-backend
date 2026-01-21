from app.core.exceptions.auth_exceptions import LoginFailError
import pytest
from unittest.mock import Mock, MagicMock, patch


def test_login_success(auth_service):
    mock_user = Mock()
    mock_user.user_id = 1
    mock_user.username = "testuser"
    mock_user.password = "hashed_password"

    auth_service.user_repo = MagicMock()
    auth_service.user_repo.find_by_username.return_value = mock_user

    with patch("app.services.auth_service.verify_password", return_value=True), patch(
        "app.services.auth_service.create_access_token", return_value="fake_token"
    ):

        result = auth_service.login("testuser", "correct_password")

        assert result == "fake_token"
        assert auth_service.user_repo.find_by_username.call_count == 1


def test_login_user_not_found(auth_service):
    auth_service.user_repo = MagicMock()
    auth_service.user_repo.find_by_username.return_value = None

    with pytest.raises(LoginFailError):
        auth_service.login("testuser", "correct_password")

    assert auth_service.user_repo.find_by_username.call_count == 1


def test_login_wrong_password(auth_service):
    mock_user = Mock()
    mock_user.user_id = 1
    mock_user.username = "testuser"
    mock_user.password = "hashed_password"

    auth_service.user_repo = MagicMock()
    auth_service.user_repo.find_by_username.return_value = mock_user

    with patch("app.services.auth_service.verify_password", return_value=False):
        with pytest.raises(LoginFailError):
            auth_service.login("testuser", "correct_password")

    assert auth_service.user_repo.find_by_username.call_count == 1
