import pytest
from unittest.mock import patch
from app.core.exceptions.auth_exceptions import LoginFailError
from app.common.errorcode import ErrorCode
from app.common.message import Message, ErrorMessage


# 正常系
def test_login_success(client):
    with patch(
        "app.services.auth_service.AuthService.login", return_value="fake_token"
    ):
        response = client.post(
            "/admin/auth/login",
            json={"username": "admin@example.com", "password": "correctpass"},
        )

    assert response.status_code == 200

    data = response.json()
    assert data["message"] == Message.LOGIN_SUCCESS
    assert data["token"] == "fake_token"


# 必須項目バリデーション
def test_validation_error_missing(client):
    response = client.post("/admin/auth/login", json={})

    assert response.status_code == 400

    data = response.json()
    messages = [item["message"] for item in data["details"]]

    assert data["error"] == ErrorCode.VALIDATION_ERROR
    assert ErrorMessage.USERNAME_REQUIRED in messages
    assert ErrorMessage.PASSWORD_REQUIRED in messages


# 最大文字数バリデーション
def test_validation_error_max_length(client):
    longtext = "a" * 51
    username = f"{longtext}@example.com"
    request = {"username": username, "password": longtext}
    response = client.post("/admin/auth/login", json=request)

    assert response.status_code == 400

    data = response.json()
    messages = [item["message"] for item in data["details"]]

    assert data["error"] == ErrorCode.VALIDATION_ERROR
    assert ErrorMessage.USERNAME_MAX_LENGTH in messages
    assert ErrorMessage.PASSWORD_MAX_LENGTH in messages


# 最小文字数バリデーション
def test_validation_error_min_length(client):
    shorttext = "a" * 7
    username = "admin@example.com"
    request = {"username": username, "password": shorttext}
    response = client.post("/admin/auth/login", json=request)

    assert response.status_code == 400

    data = response.json()
    messages = [item["message"] for item in data["details"]]

    assert data["error"] == ErrorCode.VALIDATION_ERROR
    assert ErrorMessage.PASSWORD_MIN_LENGTH in messages


# メールアドレス形式バリデーション
def test_validation_error_email_format(client):
    username = "admin"
    password = "password"
    request = {"username": username, "password": password}
    response = client.post("/admin/auth/login", json=request)

    assert response.status_code == 400

    data = response.json()
    messages = [item["message"] for item in data["details"]]

    assert data["error"] == ErrorCode.VALIDATION_ERROR
    assert ErrorMessage.USERNAME_FORMAT_EMAIL in messages


# ログインエラー
def test_login_fail_no_exist_username(client):
    username = "error@example.com"
    password = "password"
    request = {"username": username, "password": password}
    with patch(
        "app.services.auth_service.AuthService.login", side_effect=LoginFailError
    ):
        response = client.post("/admin/auth/login", json=request)

    assert response.status_code == 400

    data = response.json()

    assert data["message"] == ErrorMessage.LOGIN_FAIL
    assert data["error"] == ErrorCode.LOGIN_FAIL
