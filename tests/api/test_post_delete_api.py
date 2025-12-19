import pytest
from unittest.mock import patch
from app.common.errorcode import ErrorCode
from app.common.message import Message, ErrorMessage
from app.core.exceptions.handlers import ApplicationError


# 正常系
@patch("app.services.post_service.PostService.delete_all")
def test_delete_post_success(mock_delete_all, client, valid_token):
    mock_delete_all.return_value = None

    response = client.delete(
        "/admin/posts/1",
        headers={"Authorization": f"Bearer {valid_token}"},
    )

    assert response.status_code == 200

    body = response.json()
    assert body["message"] == Message.POST_DELETE_SUCCESS
    mock_delete_all.assert_called_once_with(1)


# パスパラメータバリデーションエラー（post_id < 1）
def test_validation_error_min_post_id(client, valid_token):
    response = client.delete(
        "/admin/posts/0",
        headers={"Authorization": f"Bearer {valid_token}"},
    )

    assert response.status_code == 400

    data = response.json()
    messages = [item["message"] for item in data["details"]]

    assert data["error"] == ErrorCode.VALIDATION_ERROR
    assert ErrorMessage.MIN_POST_ID in messages


# サービス層例外: 記事が存在しない
@patch(
    "app.services.post_service.PostService.delete_all",
    side_effect=ApplicationError(
        message=ErrorMessage.NOT_EXIST, code=ErrorCode.NOT_EXIST
    ),
)
def test_delete_post_not_exist(mock_delete_all, client, valid_token):
    response = client.delete(
        "/admin/posts/999",
        headers={"Authorization": f"Bearer {valid_token}"},
    )

    assert response.status_code == 400

    data = response.json()
    assert data["error"] == ErrorCode.NOT_EXIST
    assert data["message"] == ErrorMessage.NOT_EXIST
    mock_delete_all.assert_called_once_with(999)

