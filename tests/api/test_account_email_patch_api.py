import pytest
from unittest.mock import patch, Mock
from app.common.errorcode import ErrorCode
from app.common.message import Message, ErrorMessage
from app.common.constant import Constant
from app.core.exceptions.account_exceptions import (
    PasswordMismatchError,
    EmailMismatchError,
    EmailAlreadyExistsError,
)


# 正常系
def test_change_email_success(client, valid_token):
    mock_user = Mock()
    mock_user.user_id = 1
    mock_user.username = "new-email@example.com"

    with patch(
        "app.services.account_service.AccountService.change_email",
        return_value=mock_user,
    ):
        response = client.patch(
            "/admin/account/email",
            headers={"Authorization": f"Bearer {valid_token}"},
            json={
                "current_email": "old-email@example.com",
                "new_email": "new-email@example.com",
                "password": "password123",
            },
        )

    assert response.status_code == 200

    data = response.json()
    assert data["message"] == Message.EMAIL_CHANGE_SUCCESS
    assert data["user_id"] == 1
    assert data["username"] == "new-email@example.com"


# 必須項目バリデーション
def test_validation_error_missing(client, valid_token):
    response = client.patch(
        "/admin/account/email",
        headers={"Authorization": f"Bearer {valid_token}"},
        json={},
    )

    assert response.status_code == 400

    data = response.json()
    messages = [item["message"] for item in data["details"]]

    assert data["error"] == ErrorCode.VALIDATION_ERROR
    assert ErrorMessage.USERNAME_REQUIRED in messages
    assert ErrorMessage.PASSWORD_REQUIRED in messages


# メールアドレス形式バリデーション（current_email）
def test_validation_error_current_email_format(client, valid_token):
    response = client.patch(
        "/admin/account/email",
        headers={"Authorization": f"Bearer {valid_token}"},
        json={
            "current_email": "invalid-email",
            "new_email": "new-email@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 400

    data = response.json()
    messages = [item["message"] for item in data["details"]]

    assert data["error"] == ErrorCode.VALIDATION_ERROR
    assert ErrorMessage.USERNAME_FORMAT_EMAIL in messages


# メールアドレス形式バリデーション（new_email）
def test_validation_error_new_email_format(client, valid_token):
    response = client.patch(
        "/admin/account/email",
        headers={"Authorization": f"Bearer {valid_token}"},
        json={
            "current_email": "old-email@example.com",
            "new_email": "invalid-email",
            "password": "password123",
        },
    )

    assert response.status_code == 400

    data = response.json()
    messages = [item["message"] for item in data["details"]]

    assert data["error"] == ErrorCode.VALIDATION_ERROR
    assert ErrorMessage.USERNAME_FORMAT_EMAIL in messages


# パスワード最小文字数バリデーション
def test_validation_error_password_min_length(client, valid_token):
    small_password = "a" * (Constant.MIN_PASSWORD_LENGTH - 1)
    response = client.patch(
        "/admin/account/email",
        headers={"Authorization": f"Bearer {valid_token}"},
        json={
            "current_email": "old-email@example.com",
            "new_email": "new-email@example.com",
            "password": small_password,
        },
    )

    assert response.status_code == 400

    data = response.json()
    messages = [item["message"] for item in data["details"]]

    assert data["error"] == ErrorCode.VALIDATION_ERROR
    assert ErrorMessage.PASSWORD_MIN_LENGTH in messages


# パスワード最大文字数バリデーション
def test_validation_error_password_max_length(client, valid_token):
    big_password = "a" * (Constant.MAX_PASSWORD_LENGTH + 1)
    response = client.patch(
        "/admin/account/email",
        headers={"Authorization": f"Bearer {valid_token}"},
        json={
            "current_email": "old-email@example.com",
            "new_email": "new-email@example.com",
            "password": big_password,
        },
    )

    assert response.status_code == 400

    data = response.json()
    messages = [item["message"] for item in data["details"]]

    assert data["error"] == ErrorCode.VALIDATION_ERROR
    assert ErrorMessage.PASSWORD_MAX_LENGTH in messages


# 現在のメールアドレス不一致エラー
def test_email_mismatch_error(client, valid_token):
    with patch(
        "app.services.account_service.AccountService.change_email",
        side_effect=EmailMismatchError,
    ):
        response = client.patch(
            "/admin/account/email",
            headers={"Authorization": f"Bearer {valid_token}"},
            json={
                "current_email": "wrong-email@example.com",
                "new_email": "new-email@example.com",
                "password": "password123",
            },
        )

    assert response.status_code == 400

    data = response.json()
    assert data["message"] == ErrorMessage.EMAIL_MISMATCH
    assert data["error"] == ErrorCode.EMAIL_MISMATCH


# パスワード不一致エラー
def test_password_mismatch_error(client, valid_token):
    with patch(
        "app.services.account_service.AccountService.change_email",
        side_effect=PasswordMismatchError,
    ):
        response = client.patch(
            "/admin/account/email",
            headers={"Authorization": f"Bearer {valid_token}"},
            json={
                "current_email": "old-email@example.com",
                "new_email": "new-email@example.com",
                "password": "wrongpassword",
            },
        )

    assert response.status_code == 400

    data = response.json()
    assert data["message"] == ErrorMessage.PASSWORD_MISMATCH
    assert data["error"] == ErrorCode.PASSWORD_MISMATCH


# メールアドレス重複エラー
def test_email_already_exists_error(client, valid_token):
    with patch(
        "app.services.account_service.AccountService.change_email",
        side_effect=EmailAlreadyExistsError,
    ):
        response = client.patch(
            "/admin/account/email",
            headers={"Authorization": f"Bearer {valid_token}"},
            json={
                "current_email": "old-email@example.com",
                "new_email": "existing-email@example.com",
                "password": "password123",
            },
        )

    assert response.status_code == 400

    data = response.json()
    assert data["message"] == ErrorMessage.EMAIL_ALREADY_EXISTS
    assert data["error"] == ErrorCode.EMAIL_ALREADY_EXISTS


# トークンなしによる認証エラー
def test_not_token_authentication_error(client):
    response = client.patch(
        "/admin/account/email",
        json={
            "current_email": "old-email@example.com",
            "new_email": "new-email@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 401

    data = response.json()
    assert data["message"] == ErrorMessage.TOKEN_REQUIRED
