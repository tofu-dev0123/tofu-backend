import pytest
from app.core.message import Message, ErrorMessage


# 正常系
def test_me_success(client, valid_token):
    response = client.post(
        "/admin/auth/me", headers={"Authorization": f"Bearer {valid_token}"}
    )

    assert response.status_code == 200

    data = response.json()
    assert data["userId"] == 1
    assert data["username"] == "test@example.com"
    assert data["accountName"] == "testuser"
