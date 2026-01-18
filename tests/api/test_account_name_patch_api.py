import pytest
from app.common.errorcode import ErrorCode
from app.common.message import Message, ErrorMessage
from app.common.constant import Constant


# 正常系
def test_update_account_name_success(client, valid_token):
    response = client.patch(
        "/admin/account",
        headers={"Authorization": f"Bearer {valid_token}"},
        json={"account_name": "新しいアカウント名"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["message"] == Message.ACCOUNT_UPDATE_SUCCESS
    assert data["user_id"] == 1
    assert data["account_name"] == "新しいアカウント名"


# 必須項目バリデーション
def test_validation_error_missing(client, valid_token):
    response = client.patch(
        "/admin/account",
        headers={"Authorization": f"Bearer {valid_token}"},
        json={},
    )

    assert response.status_code == 400

    data = response.json()
    messages = [item["message"] for item in data["details"]]

    assert data["error"] == ErrorCode.VALIDATION_ERROR
    assert ErrorMessage.ACCOUNT_NAME_REQUIRED in messages


# 最大文字数バリデーション
def test_validation_error_max_length(client, valid_token):
    big_account_name = "あ" * (Constant.MAX_ACCOUNT_NAME_LENGTH + 1)
    response = client.patch(
        "/admin/account",
        headers={"Authorization": f"Bearer {valid_token}"},
        json={"account_name": big_account_name},
    )

    assert response.status_code == 400

    data = response.json()
    messages = [item["message"] for item in data["details"]]

    assert data["error"] == ErrorCode.VALIDATION_ERROR
    assert ErrorMessage.ACCOUNT_NAME_MAX_LENGTH in messages


# 空白のみバリデーション
def test_validation_error_blank_only(client, valid_token):
    response = client.patch(
        "/admin/account",
        headers={"Authorization": f"Bearer {valid_token}"},
        json={"account_name": "   "},
    )

    assert response.status_code == 400

    data = response.json()
    messages = [item["message"] for item in data["details"]]

    assert data["error"] == ErrorCode.VALIDATION_ERROR
    assert ErrorMessage.ACCOUNT_NAME_BLANK in messages


# トークンなしによる認証エラー
def test_not_token_authentication_error(client):
    response = client.patch(
        "/admin/account",
        json={"account_name": "新しいアカウント名"},
    )

    assert response.status_code == 401

    data = response.json()
    assert data["message"] == ErrorMessage.TOKEN_REQUIRED
