from unittest.mock import patch
from app.common.errorcode import ErrorCode
from app.common.message import Message, ErrorMessage
from app.common.constant import Constant
from app.schemas.profile import ProfileResponse


# 正常系: プロフィール取得
@patch("app.services.profile_service.ProfileService.get_profile")
def test_get_profile_success(mock_get_profile, client, valid_token):
    mock_get_profile.return_value = ProfileResponse(
        headline="Webエンジニア", bio="自己紹介", site_description="サイト説明"
    )

    response = client.get(
        "/admin/profile", headers={"Authorization": f"Bearer {valid_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["headline"] == "Webエンジニア"
    assert data["bio"] == "自己紹介"
    assert data["site_description"] == "サイト説明"


# 異常系: トークンなし
def test_get_profile_no_token(client):
    response = client.get("/admin/profile")

    assert response.status_code == 401


# 正常系: プロフィール更新
@patch("app.services.profile_service.ProfileService.update_profile")
def test_update_profile_success(mock_update_profile, client, valid_token):
    mock_update_profile.return_value = None

    req = {"headline": "new", "bio": "new bio", "site_description": "new desc"}
    response = client.put(
        "/admin/profile",
        headers={"Authorization": f"Bearer {valid_token}"},
        json=req,
    )

    assert response.status_code == 200
    assert response.json()["message"] == Message.PROFILE_UPDATE_SUCCESS


# バリデーションエラー: headline 最大文字数超過
def test_update_profile_validation_headline_max(client, valid_token):
    req = {
        "headline": "a" * (Constant.MAX_HEADLINE_LENGTH + 1),
        "bio": "b",
        "site_description": "s",
    }
    response = client.put(
        "/admin/profile",
        headers={"Authorization": f"Bearer {valid_token}"},
        json=req,
    )

    assert response.status_code == 400
    data = response.json()
    messages = [item["message"] for item in data["details"]]
    assert data["error"] == ErrorCode.VALIDATION_ERROR
    assert ErrorMessage.HEADLINE_MAX_LENGTH in messages


# バリデーションエラー: 必須項目欠落
def test_update_profile_validation_missing(client, valid_token):
    response = client.put(
        "/admin/profile",
        headers={"Authorization": f"Bearer {valid_token}"},
        json={},
    )

    assert response.status_code == 400
    data = response.json()
    messages = [item["message"] for item in data["details"]]
    assert data["error"] == ErrorCode.VALIDATION_ERROR
    assert ErrorMessage.HEADLINE_REQUIRED in messages
    assert ErrorMessage.BIO_REQUIRED in messages
    assert ErrorMessage.SITE_DESCRIPTION_REQUIRED in messages
