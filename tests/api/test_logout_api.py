import pytest
from app.core.message import Message, ErrorMessage


# 正常系
def test_logout_success(client, valid_token):
    response = client.post(
        "/admin/auth/logout", headers={"Authorization": f"Bearer {valid_token}"}
    )

    assert response.status_code == 200

    data = response.json()
    assert data["message"] == Message.LOGOUT_SUCCESS


# トークンなしによる認証エラー
def test_not_token_authentication_error(client):
    response = client.post("/admin/auth/logout")

    assert response.status_code == 401

    data = response.json()
    assert data["message"] == ErrorMessage.TOKEN_REQUIRED
