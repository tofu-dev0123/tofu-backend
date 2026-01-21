import pytest
from unittest.mock import patch
from app.common.errorcode import ErrorCode
from app.common.message import Message, ErrorMessage
from app.common.constant import Constant
from app.core.exceptions.account_exceptions import PasswordMismatchError


# 正常系
def test_change_password_success(client, valid_token):
    with patch(
        "app.services.account_service.AccountService.change_password",
        return_value=None,
    ):
        response = client.patch(
            "/admin/account/password",
            headers={"Authorization": f"Bearer {valid_token}"},
            json={
                "current_password": "oldpassword123",
                "new_password": "newpassword456",
            },
        )

    assert response.status_code == 200

    data = response.json()
    assert data["message"] == Message.PASSWORD_CHANGE_SUCCESS


# 必須項目バリデーション
def test_validation_error_missing(client, valid_token):
    response = client.patch(
        "/admin/account/password",
        headers={"Authorization": f"Bearer {valid_token}"},
        json={},
    )

    assert response.status_code == 400

    data = response.json()
    messages = [item["message"] for item in data["details"]]

    assert data["error"] == ErrorCode.VALIDATION_ERROR
    assert ErrorMessage.PASSWORD_REQUIRED in messages


# 最小文字数バリデーション（current_password）
def test_validation_error_current_password_min_length(client, valid_token):
    small_password = "a" * (Constant.MIN_PASSWORD_LENGTH - 1)
    response = client.patch(
        "/admin/account/password",
        headers={"Authorization": f"Bearer {valid_token}"},
        json={
            "current_password": small_password,
            "new_password": "newpassword456",
        },
    )

    assert response.status_code == 400

    data = response.json()
    messages = [item["message"] for item in data["details"]]

    assert data["error"] == ErrorCode.VALIDATION_ERROR
    assert ErrorMessage.PASSWORD_MIN_LENGTH in messages


# 最小文字数バリデーション（new_password）
def test_validation_error_new_password_min_length(client, valid_token):
    small_password = "a" * (Constant.MIN_PASSWORD_LENGTH - 1)
    response = client.patch(
        "/admin/account/password",
        headers={"Authorization": f"Bearer {valid_token}"},
        json={
            "current_password": "oldpassword123",
            "new_password": small_password,
        },
    )

    assert response.status_code == 400

    data = response.json()
    messages = [item["message"] for item in data["details"]]

    assert data["error"] == ErrorCode.VALIDATION_ERROR
    assert ErrorMessage.PASSWORD_MIN_LENGTH in messages


# 最大文字数バリデーション
def test_validation_error_max_length(client, valid_token):
    big_password = "a" * (Constant.MAX_PASSWORD_LENGTH + 1)
    response = client.patch(
        "/admin/account/password",
        headers={"Authorization": f"Bearer {valid_token}"},
        json={
            "current_password": big_password,
            "new_password": big_password,
        },
    )

    assert response.status_code == 400

    data = response.json()
    messages = [item["message"] for item in data["details"]]

    assert data["error"] == ErrorCode.VALIDATION_ERROR
    assert ErrorMessage.PASSWORD_MAX_LENGTH in messages


# 現在のパスワード不一致エラー
def test_password_mismatch_error(client, valid_token):
    with patch(
        "app.services.account_service.AccountService.change_password",
        side_effect=PasswordMismatchError,
    ):
        response = client.patch(
            "/admin/account/password",
            headers={"Authorization": f"Bearer {valid_token}"},
            json={
                "current_password": "wrongpassword",
                "new_password": "newpassword456",
            },
        )

    assert response.status_code == 400

    data = response.json()
    assert data["message"] == ErrorMessage.PASSWORD_MISMATCH
    assert data["error"] == ErrorCode.PASSWORD_MISMATCH


# トークンなしによる認証エラー
def test_not_token_authentication_error(client):
    response = client.patch(
        "/admin/account/password",
        json={
            "current_password": "oldpassword123",
            "new_password": "newpassword456",
        },
    )

    assert response.status_code == 401

    data = response.json()
    assert data["message"] == ErrorMessage.TOKEN_REQUIRED
