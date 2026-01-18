import pytest
from unittest.mock import Mock, MagicMock, patch
from app.core.exceptions.account_exceptions import (
    PasswordMismatchError,
    EmailMismatchError,
    EmailAlreadyExistsError,
)


# ==================== update_account_name ====================


def test_update_account_name_success(account_service):
    mock_user = Mock()
    mock_user.user_id = 1
    mock_user.account_name = "old_name"

    updated_user = Mock()
    updated_user.user_id = 1
    updated_user.account_name = "new_name"

    account_service.user_repo = MagicMock()
    account_service.user_repo.update_account_name.return_value = updated_user

    result = account_service.update_account_name(mock_user, "new_name")

    assert result.account_name == "new_name"
    assert account_service.user_repo.update_account_name.call_count == 1
    account_service.user_repo.update_account_name.assert_called_once_with(
        mock_user, "new_name"
    )


# ==================== change_password ====================


def test_change_password_success(account_service):
    mock_user = Mock()
    mock_user.user_id = 1
    mock_user.password = "hashed_old_password"

    account_service.user_repo = MagicMock()

    with patch(
        "app.services.account_service.verify_password", return_value=True
    ), patch(
        "app.services.account_service.hash_password",
        return_value="hashed_new_password",
    ):
        account_service.change_password(mock_user, "old_password", "new_password")

    assert account_service.user_repo.update_password.call_count == 1
    account_service.user_repo.update_password.assert_called_once_with(
        mock_user, "hashed_new_password"
    )


def test_change_password_wrong_current_password(account_service):
    mock_user = Mock()
    mock_user.user_id = 1
    mock_user.password = "hashed_old_password"

    account_service.user_repo = MagicMock()

    with patch("app.services.account_service.verify_password", return_value=False):
        with pytest.raises(PasswordMismatchError):
            account_service.change_password(mock_user, "wrong_password", "new_password")

    assert account_service.user_repo.update_password.call_count == 0


# ==================== change_email ====================


def test_change_email_success(account_service):
    mock_user = Mock()
    mock_user.user_id = 1
    mock_user.username = "old@example.com"
    mock_user.password = "hashed_password"

    updated_user = Mock()
    updated_user.user_id = 1
    updated_user.username = "new@example.com"

    account_service.user_repo = MagicMock()
    account_service.user_repo.exists_by_username.return_value = False
    account_service.user_repo.update_email.return_value = updated_user

    with patch("app.services.account_service.verify_password", return_value=True):
        result = account_service.change_email(
            mock_user, "old@example.com", "new@example.com", "password"
        )

    assert result.username == "new@example.com"
    assert account_service.user_repo.exists_by_username.call_count == 1
    assert account_service.user_repo.update_email.call_count == 1


def test_change_email_wrong_current_email(account_service):
    mock_user = Mock()
    mock_user.user_id = 1
    mock_user.username = "current@example.com"
    mock_user.password = "hashed_password"

    account_service.user_repo = MagicMock()

    with pytest.raises(EmailMismatchError):
        account_service.change_email(
            mock_user, "wrong@example.com", "new@example.com", "password"
        )

    assert account_service.user_repo.update_email.call_count == 0


def test_change_email_wrong_password(account_service):
    mock_user = Mock()
    mock_user.user_id = 1
    mock_user.username = "current@example.com"
    mock_user.password = "hashed_password"

    account_service.user_repo = MagicMock()

    with patch("app.services.account_service.verify_password", return_value=False):
        with pytest.raises(PasswordMismatchError):
            account_service.change_email(
                mock_user, "current@example.com", "new@example.com", "wrong_password"
            )

    assert account_service.user_repo.update_email.call_count == 0


def test_change_email_already_exists(account_service):
    mock_user = Mock()
    mock_user.user_id = 1
    mock_user.username = "current@example.com"
    mock_user.password = "hashed_password"

    account_service.user_repo = MagicMock()
    account_service.user_repo.exists_by_username.return_value = True

    with patch("app.services.account_service.verify_password", return_value=True):
        with pytest.raises(EmailAlreadyExistsError):
            account_service.change_email(
                mock_user, "current@example.com", "existing@example.com", "password"
            )

    assert account_service.user_repo.exists_by_username.call_count == 1
    assert account_service.user_repo.update_email.call_count == 0
