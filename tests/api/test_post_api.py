import pytest
from app.schemas.post import PostsPostRequest
from unittest.mock import patch
from app.core.exceptions.auth_exceptions import LoginFailError
from app.common.errorcode import ErrorCode
from app.common.message import Message, ErrorMessage
from app.common.constant import Constant


# 正常系
@patch("app.services.post_service.PostService.create_all")
def test_login_success(mock_create_all, client, valid_token):
    mock_create_all.return_value = 1
    req = {
        "title": "Test",
        "content_md": "test_md",
        "content_html": "test_html",
        "thumbnail_url": "test_thumb",
        "status": "PUBLISHED",
        "tags": ["python", "fastapi"],
        "images": [1, 2]
    }
    response = client.post(
        "/admin/posts",
        headers={"Authorization": f"Bearer {valid_token}"},
        json=req,
    )

    assert response.status_code == 200

    data = response.json()
    assert data["message"] == Message.POST_CREATE_SUCCESS
    assert data["post_id"] == 1


# 必須項目バリデーションエラー
def test_validation_error_missing(client, valid_token):
    response = client.post(
        "/admin/posts",
        headers={"Authorization": f"Bearer {valid_token}"},
        json={}
    )

    assert response.status_code == 400

    data = response.json()
    messages = [item["message"] for item in data["details"]]

    assert data["error"] == ErrorCode.VALIDATION_ERROR
    assert ErrorMessage.TITLE_REQUIRED in messages
    assert ErrorMessage.CONTENT_MARKDOWN_REQUIRED in messages
    assert ErrorMessage.CONTENT_HTML_REQUIRED in messages
    assert ErrorMessage.STATUS_REQUIRED in messages


# 最大文字数バリデーションエラー
def test_validation_error_max_length(client, valid_token):
    big_title = "a" * (Constant.MAX_TITLE_LENGTH + 1)
    big_url = "a" * (Constant.MAX_THUMBNAIL_URL + 1)
    big_content_md = "a" * (Constant.MAX_CONTENT_MARKDOWN_SIZE + 1)
    big_tag = "a" * (Constant.MAX_TAG_LENGTH + 1)
    big_tags = [big_tag]
    req = {
        "title": big_title,
        "content_md": big_content_md,
        "content_html": "test_html",
        "thumbnail_url": big_url,
        "status": "PUBLISHED",
        "tags": big_tags
    }
    response = client.post(
        "/admin/posts",
        headers={"Authorization": f"Bearer {valid_token}"},
        json=req
    )

    assert response.status_code == 400

    data = response.json()
    messages = [item["message"] for item in data["details"]]

    assert data["error"] == ErrorCode.VALIDATION_ERROR
    assert ErrorMessage.TITLE_MAX_LENGTH in messages
    assert ErrorMessage.THUMBNAIL_URL_MAX_LENGTH in messages
    assert ErrorMessage.CONTENT_MARKDOWN_SIZE_OVER in messages
    assert ErrorMessage.TAGS_MAX_LENGTH in messages

# 配列最大個数バリデーションエラー
def test_validation_error_max_array(client, valid_token):
    big_tags = ["a"] * (Constant.MAX_TAGS + 1)
    req = {
        "title": "Test",
        "content_md": "test_md",
        "content_html": "test_html",
        "thumbnail_url": "test_thumb",
        "status": "PUBLISHED",
        "tags": big_tags
    }
    response = client.post(
        "/admin/posts",
        headers={"Authorization": f"Bearer {valid_token}"},
        json=req
    )

    assert response.status_code == 400

    data = response.json()
    messages = [item["message"] for item in data["details"]]

    assert data["error"] == ErrorCode.VALIDATION_ERROR
    assert ErrorMessage.TAGS_ARRAY_MAX_LENGTH in messages