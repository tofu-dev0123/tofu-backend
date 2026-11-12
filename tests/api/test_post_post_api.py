import pytest
from unittest.mock import patch
from app.common.errorcode import ErrorCode
from app.common.message import Message, ErrorMessage
from app.common.constant import Constant
from app.core.exceptions.post_exceptions import SlugAlreadyExistsError


# 正常系
@patch("app.services.post_service.PostService.create_all")
def test_create_post_success(mock_create_all, client, auth_headers):
    mock_create_all.return_value = 1
    req = {
        "title": "Test",
        "content_md": "test_md",
        "thumbnail_url": "test_thumb",
        "status": "PUBLISHED",
        "tags": ["python", "fastapi"],
        "images": [1, 2],
    }
    response = client.post(
        "/admin/posts",
        headers=auth_headers,
        json=req,
    )

    assert response.status_code == 200

    data = response.json()
    assert data["message"] == Message.POST_CREATE_SUCCESS
    assert data["post_id"] == 1


# 必須項目バリデーションエラー
def test_validation_error_missing(client, auth_headers):
    response = client.post(
        "/admin/posts", headers=auth_headers, json={}
    )

    assert response.status_code == 400

    data = response.json()
    messages = [item["message"] for item in data["details"]]

    assert data["error"] == ErrorCode.VALIDATION_ERROR
    assert ErrorMessage.CONTENT_MARKDOWN_REQUIRED in messages
    assert ErrorMessage.STATUS_REQUIRED in messages


# 最大文字数バリデーションエラー
def test_validation_error_max_length(client, auth_headers):
    big_title = "a" * (Constant.MAX_TITLE_LENGTH + 1)
    big_url = "a" * (Constant.MAX_THUMBNAIL_URL + 1)
    big_content_md = "a" * (Constant.MAX_CONTENT_MARKDOWN_SIZE + 1)
    big_tag = "a" * (Constant.MAX_TAG_LENGTH + 1)
    big_tags = [big_tag]
    req = {
        "title": big_title,
        "content_md": big_content_md,
        "thumbnail_url": big_url,
        "status": "PUBLISHED",
        "tags": big_tags,
    }
    response = client.post(
        "/admin/posts", headers=auth_headers, json=req
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
def test_validation_error_max_array(client, auth_headers):
    big_tags = ["a"] * (Constant.MAX_TAGS + 1)
    req = {
        "title": "Test",
        "content_md": "test_md",
        "thumbnail_url": "test_thumb",
        "status": "PUBLISHED",
        "tags": big_tags,
    }
    response = client.post(
        "/admin/posts", headers=auth_headers, json=req
    )

    assert response.status_code == 400

    data = response.json()
    messages = [item["message"] for item in data["details"]]

    assert data["error"] == ErrorCode.VALIDATION_ERROR
    assert ErrorMessage.TAGS_ARRAY_MAX_LENGTH in messages


# スラグ指定ありの正常系
@patch("app.services.post_service.PostService.create_all")
def test_create_post_with_slug_success(mock_create_all, client, auth_headers):
    mock_create_all.return_value = 1
    req = {
        "title": "Test",
        "slug": "my-first-post-2",
        "content_md": "test_md",
        "status": "PUBLISHED",
    }
    response = client.post("/admin/posts", headers=auth_headers, json=req)

    assert response.status_code == 200
    request = mock_create_all.call_args.args[0]
    assert request.slug == "my-first-post-2"


# スラグ空文字は未入力扱い
@patch("app.services.post_service.PostService.create_all")
def test_create_post_with_empty_slug(mock_create_all, client, auth_headers):
    mock_create_all.return_value = 1
    req = {"title": "Test", "slug": "", "content_md": "test_md", "status": "DRAFT"}
    response = client.post("/admin/posts", headers=auth_headers, json=req)

    assert response.status_code == 200
    request = mock_create_all.call_args.args[0]
    assert request.slug is None


# スラグ形式バリデーションエラー
@pytest.mark.parametrize(
    "slug", ["Upper-Case", "with space", "under_score", "-leading", "trailing-", "double--hyphen", "日本語"]
)
def test_validation_error_slug_format(client, auth_headers, slug):
    req = {"title": "Test", "slug": slug, "content_md": "test_md", "status": "DRAFT"}
    response = client.post("/admin/posts", headers=auth_headers, json=req)

    assert response.status_code == 400
    data = response.json()
    messages = [item["message"] for item in data["details"]]
    assert data["error"] == ErrorCode.VALIDATION_ERROR
    assert ErrorMessage.SLUG_FORMAT in messages


# スラグ最大文字数バリデーションエラー
def test_validation_error_slug_max_length(client, auth_headers):
    req = {
        "title": "Test",
        "slug": "a" * (Constant.MAX_SLUG_LENGTH + 1),
        "content_md": "test_md",
        "status": "DRAFT",
    }
    response = client.post("/admin/posts", headers=auth_headers, json=req)

    assert response.status_code == 400
    data = response.json()
    messages = [item["message"] for item in data["details"]]
    assert data["error"] == ErrorCode.VALIDATION_ERROR
    assert ErrorMessage.SLUG_MAX_LENGTH in messages


# スラグ重複エラー
@patch(
    "app.services.post_service.PostService.create_all",
    side_effect=SlugAlreadyExistsError,
)
def test_create_post_slug_already_exists(mock_create_all, client, auth_headers):
    req = {"title": "Test", "slug": "dup", "content_md": "test_md", "status": "DRAFT"}
    response = client.post("/admin/posts", headers=auth_headers, json=req)

    assert response.status_code == 400
    data = response.json()
    assert data["error"] == ErrorCode.SLUG_ALREADY_EXISTS
    assert data["message"] == ErrorMessage.SLUG_ALREADY_EXISTS
