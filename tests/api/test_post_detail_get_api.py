import pytest
from unittest.mock import patch, Mock
from datetime import datetime
from app.common.errorcode import ErrorCode
from app.common.message import Message, ErrorMessage
from app.common.constant import Constant
from app.models.post import PostStatus
from app.schemas.post import PostGetResponse


# 正常系
@patch("app.services.post_service.PostService.get_post_detail")
def test_login_success(mock_get_detail, client, valid_token):
    mock_get_detail.return_value = PostGetResponse(
        post_id=1,
        title="テストタイトル",
        slug="test-slug",
        content_md="markdown",
        content_html="<p>html</p>",
        thumbnail_url="https://example.com/thumb.png",
        status=PostStatus.PUBLISHED,
        images=[],
        tags=[],
        published_at=datetime(2025, 1, 1),
        created_at=datetime(2025, 1, 1),
        updated_at=datetime(2025, 1, 2),
    )

    response = client.get(
        "/admin/posts/1",
        headers={"Authorization": f"Bearer {valid_token}"},
    )

    assert response.status_code == 200
    mock_get_detail.assert_called_once()


# 最小値バリデーションエラー
def test_validation_error_min(client, valid_token):
    response = client.get(
        "/admin/posts/-1",
        headers={"Authorization": f"Bearer {valid_token}"},
    )

    assert response.status_code == 400

    data = response.json()
    messages = [item["message"] for item in data["details"]]

    assert data["error"] == ErrorCode.VALIDATION_ERROR
    assert ErrorMessage.MIN_POST_ID in messages
