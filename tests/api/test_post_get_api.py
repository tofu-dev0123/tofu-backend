import pytest
from unittest.mock import patch
from app.common.errorcode import ErrorCode
from app.common.message import ErrorMessage
from app.common.constant import Constant


# 正常系
@patch("app.services.post_service.PostService.get_posts")
def test_get_posts_success(mock_create_all, client, valid_token):
    res = {"total_count": 1, "total_pages": 1, "posts": []}
    mock_create_all.return_value = res

    response = client.get(
        "/admin/posts",
        headers={"Authorization": f"Bearer {valid_token}"},
    )

    assert response.status_code == 200

    data = response.json()
    assert "total_count" in data
    assert "total_pages" in data
    assert "posts" in data


# 最大文字数バリデーションエラー
def test_validation_error_max_length(client, valid_token):
    response = client.get(
        "/admin/posts",
        headers={"Authorization": f"Bearer {valid_token}"},
        params={
            "keyword": "a" * (Constant.MAX_KEYWORD_LENGTH + 1),
            "limit": Constant.MAX_LIMIT + 1,
        },
    )

    assert response.status_code == 400

    data = response.json()
    messages = [item["message"] for item in data["details"]]

    assert data["error"] == ErrorCode.VALIDATION_ERROR
    assert ErrorMessage.KEYWORD_MAX_LENGTH in messages
    assert ErrorMessage.MAX_LIMIT in messages


# 最小文字数バリデーションエラー
def test_validation_error_min_length(client, valid_token):
    response = client.get(
        "/admin/posts",
        headers={"Authorization": f"Bearer {valid_token}"},
        params={"offset": Constant.MIN_OFFSET - 1, "limit": Constant.MIN_LIMIT - 1},
    )

    assert response.status_code == 400

    data = response.json()
    messages = [item["message"] for item in data["details"]]

    assert data["error"] == ErrorCode.VALIDATION_ERROR
    assert ErrorMessage.MIN_OFFSET in messages
    assert ErrorMessage.MIN_LIMIT in messages
