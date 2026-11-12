# 正常系
def test_me_success(client, auth_headers):
    response = client.post(
        "/admin/auth/me", headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()
    assert data["user_id"] == 1
    assert data["username"] == "test@example.com"
    assert data["account_name"] == "testuser"


# get_current_user を差し替えると DB なしで認証済みとして扱える
def test_me_with_override_current_user(client, override_current_user):
    response = client.post("/admin/auth/me")

    assert response.status_code == 200

    data = response.json()
    assert data["user_id"] == override_current_user.user_id
    assert data["username"] == override_current_user.username
    assert data["account_name"] == override_current_user.account_name
