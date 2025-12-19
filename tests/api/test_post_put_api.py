import pytest
from unittest.mock import patch
from app.common.errorcode import ErrorCode
from app.common.message import Message, ErrorMessage
from app.common.constant import Constant
from app.core.exceptions.image_exceptions import ImageNotExistError
from app.core.exceptions.handlers import ApplicationError


# 正常系
@patch("app.services.post_service.PostService.update_all")
def test_update_post_success(mock_update_all, client, valid_token):
    mock_update_all.return_value = None
    req = {
        "title": "Updated Test",
        "content_md": "updated_md",
        "content_html": "updated_html",
        "thumbnail_url": "https://example.com/new-thumb.png",
        "thumbnail_delete_flag": False,
        "status": "PUBLISHED",
        "delete_images": [1, 2],
        "new_images": [3, 4],
        "tags": ["python", "django"],
    }
    response = client.put(
        "/admin/posts/999",
        headers={"Authorization": f"Bearer {valid_token}"},
        json=req,
    )

    assert response.status_code == 200

    data = response.json()
    assert data["message"] == Message.POST_UPDATE_SUCCESS
    assert data["post_id"] == 999
    mock_update_all.assert_called_once()


# 必須項目バリデーションエラー
def test_validation_error_missing(client, valid_token):
    response = client.put(
        "/admin/posts/1",
        headers={"Authorization": f"Bearer {valid_token}"},
        json={},
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
        "thumbnail_delete_flag": False,
        "status": "PUBLISHED",
        "tags": big_tags,
    }
    response = client.put(
        "/admin/posts/1",
        headers={"Authorization": f"Bearer {valid_token}"},
        json=req,
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
        "thumbnail_delete_flag": False,
        "status": "PUBLISHED",
        "tags": big_tags,
    }
    response = client.put(
        "/admin/posts/1",
        headers={"Authorization": f"Bearer {valid_token}"},
        json=req,
    )

    assert response.status_code == 400

    data = response.json()
    messages = [item["message"] for item in data["details"]]

    assert data["error"] == ErrorCode.VALIDATION_ERROR
    assert ErrorMessage.TAGS_ARRAY_MAX_LENGTH in messages


# パスパラメータバリデーションエラー（post_id < 1）
def test_validation_error_min_post_id(client, valid_token):
    req = {
        "title": "Test",
        "content_md": "test_md",
        "content_html": "test_html",
        "thumbnail_delete_flag": False,
        "status": "PUBLISHED",
    }
    response = client.put(
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
    "app.services.post_service.PostService.update_all",
    side_effect=ApplicationError(
        message=ErrorMessage.NOT_EXIST, code=ErrorCode.NOT_EXIST
    ),
)
def test_update_post_not_exist(mock_update_all, client, valid_token):
    req = {
        "title": "Test",
        "content_md": "test_md",
        "content_html": "test_html",
        "thumbnail_delete_flag": False,
        "status": "PUBLISHED",
    }
    response = client.put(
        "/admin/posts/999",
        headers={"Authorization": f"Bearer {valid_token}"},
        json=req,
    )

    assert response.status_code == 400

    data = response.json()
    assert data["error"] == ErrorCode.NOT_EXIST
    assert data["message"] == ErrorMessage.NOT_EXIST
    mock_update_all.assert_called_once()


# サービス層例外: サムネイル削除フラグとURLの矛盾
@patch(
    "app.services.post_service.PostService.update_all",
    side_effect=ApplicationError(
        message=ErrorMessage.BAD_REQUEST_OF_THUMBNAIL,
        code=ErrorCode.BAD_REQUEST_OF_THUMBNAIL,
    ),
)
def test_update_post_bad_request_of_thumbnail(mock_update_all, client, valid_token):
    req = {
        "title": "Test",
        "content_md": "test_md",
        "content_html": "test_html",
        "thumbnail_url": "https://example.com/new.png",
        "thumbnail_delete_flag": True,
        "status": "PUBLISHED",
    }
    response = client.put(
        "/admin/posts/1",
        headers={"Authorization": f"Bearer {valid_token}"},
        json=req,
    )

    assert response.status_code == 400

    data = response.json()
    assert data["error"] == ErrorCode.BAD_REQUEST_OF_THUMBNAIL
    assert data["message"] == ErrorMessage.BAD_REQUEST_OF_THUMBNAIL
    mock_update_all.assert_called_once()


# サービス層例外: 画像の所有者が異なる
@patch(
    "app.services.post_service.PostService.update_all",
    side_effect=ApplicationError(
        message=ErrorMessage.INVALID_IMAGE_OWNER.format(image_id=999),
        code=ErrorCode.INVALID_IMAGE_OWNER,
    ),
)
def test_update_post_invalid_image_owner(mock_update_all, client, valid_token):
    req = {
        "title": "Test",
        "content_md": "test_md",
        "content_html": "test_html",
        "thumbnail_delete_flag": False,
        "status": "PUBLISHED",
        "delete_images": [999],
    }
    response = client.put(
        "/admin/posts/1",
        headers={"Authorization": f"Bearer {valid_token}"},
        json=req,
    )

    assert response.status_code == 400

    data = response.json()
    assert data["error"] == ErrorCode.INVALID_IMAGE_OWNER
    assert data["message"] == ErrorMessage.INVALID_IMAGE_OWNER.format(image_id=999)
    mock_update_all.assert_called_once()


# サービス層例外: 削除対象の画像が存在しない
@patch(
    "app.services.post_service.PostService.update_all",
    side_effect=ImageNotExistError(),
)
def test_update_post_image_not_exist(mock_update_all, client, valid_token):
    req = {
        "title": "Test",
        "content_md": "test_md",
        "content_html": "test_html",
        "thumbnail_delete_flag": False,
        "status": "PUBLISHED",
        "delete_images": [999],
    }
    response = client.put(
        "/admin/posts/1",
        headers={"Authorization": f"Bearer {valid_token}"},
        json=req,
    )

    assert response.status_code == 400

    data = response.json()
    assert data["error"] == ErrorCode.NOT_EXIST
    mock_update_all.assert_called_once()
