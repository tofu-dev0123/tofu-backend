import pytest
from unittest.mock import patch
from app.common.errorcode import ErrorCode
from app.common.message import Message, ErrorMessage
from app.core.exceptions.handlers import ApplicationError
from app.models.post import PostStatus


# 正常系
@patch("app.services.post_service.PostService.patch_status")
def test_patch_status_success(mock_patch_status, client, valid_token):
    mock_patch_status.return_value = None
    req = {"status": "PUBLISHED"}
    response = client.patch(
        "/admin/posts/999",
        headers={"Authorization": f"Bearer {valid_token}"},
        json=req,
    )

    assert response.status_code == 200

    data = response.json()
    assert data["message"] == Message.POST_PATCH_SUCCESS.format(status="PUBLISHED")
    mock_patch_status.assert_called_once_with(PostStatus.PUBLISHED, 999)


# 必須項目バリデーションエラー（statusが未指定）
def test_validation_error_missing_status(client, valid_token):
    response = client.patch(
        "/admin/posts/1",
        headers={"Authorization": f"Bearer {valid_token}"},
        json={},
    )

    assert response.status_code == 400

    data = response.json()
    messages = [item["message"] for item in data["details"]]

    assert data["error"] == ErrorCode.VALIDATION_ERROR
    assert ErrorMessage.STATUS_REQUIRED in messages


# パスパラメータバリデーションエラー（post_id < 1）
def test_validation_error_min_post_id(client, valid_token):
    req = {"status": "PUBLISHED"}
    response = client.patch(
        "/admin/posts/0",
        headers={"Authorization": f"Bearer {valid_token}"},
        json=req,
    )

    assert response.status_code == 400

    data = response.json()
    messages = [item["message"] for item in data["details"]]

    assert data["error"] == ErrorCode.VALIDATION_ERROR
    assert ErrorMessage.MIN_POST_ID in messages


# サービス層例外: 記事が存在しない
@patch(
    "app.services.post_service.PostService.patch_status",
    side_effect=ApplicationError(
        message=ErrorMessage.NOT_EXIST, code=ErrorCode.NOT_EXIST
    ),
)
def test_patch_status_not_exist(mock_patch_status, client, valid_token):
    req = {"status": "PUBLISHED"}
    response = client.patch(
        "/admin/posts/999",
        headers={"Authorization": f"Bearer {valid_token}"},
        json=req,
    )

    assert response.status_code == 400

    data = response.json()
    assert data["error"] == ErrorCode.NOT_EXIST
    assert data["message"] == ErrorMessage.NOT_EXIST
    mock_patch_status.assert_called_once_with(PostStatus.PUBLISHED, 999)


# 正常系: DRAFTステータス
@patch("app.services.post_service.PostService.patch_status")
def test_patch_status_draft_success(mock_patch_status, client, valid_token):
    mock_patch_status.return_value = None
    req = {"status": "DRAFT"}
    response = client.patch(
        "/admin/posts/999",
        headers={"Authorization": f"Bearer {valid_token}"},
        json=req,
    )

    assert response.status_code == 200

    data = response.json()
    assert data["message"] == Message.POST_PATCH_SUCCESS.format(status="DRAFT")
    mock_patch_status.assert_called_once_with(PostStatus.DRAFT, 999)
