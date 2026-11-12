from app.common.message import Message, ErrorMessage
from app.common.errorcode import ErrorCode


# 正常系
def test_logout_success(client, auth_headers):
    response = client.post(
        "/admin/auth/logout", headers=auth_headers
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

    assert data["error"] == ErrorCode.AUTHENTICATION_ERROR


# 不正なトークンによる認証エラー
def test_invalid_token_authentication_error(client):
    response = client.post(
        "/admin/auth/logout", headers={"Authorization": "Bearer invalid-token"}
    )

    assert response.status_code == 401

    data = response.json()
    assert data["message"] == ErrorMessage.AUTHENTICATION_ERROR
    assert data["error"] == ErrorCode.AUTHENTICATION_ERROR
