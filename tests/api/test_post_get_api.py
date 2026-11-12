from datetime import datetime
from unittest.mock import patch
from app.common.errorcode import ErrorCode
from app.common.message import ErrorMessage
from app.common.constant import Constant
from app.models.post import PostStatus
from app.schemas.post import Post, PostsListGetResponse


# 正常系
@patch("app.services.post_service.PostService.get_posts")
def test_get_posts_success(mock_create_all, client, auth_headers):
    res = {"total_count": 1, "total_pages": 1, "posts": []}
    mock_create_all.return_value = res

    response = client.get(
        "/admin/posts",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()
    assert "total_count" in data
    assert "total_pages" in data
    assert "posts" in data


# レスポンスの日時キーが snake_case である
@patch("app.services.post_service.PostService.get_posts")
def test_get_posts_response_keys_snake_case(mock_get_posts, client, auth_headers):
    mock_get_posts.return_value = PostsListGetResponse(
        total_count=1,
        total_pages=1,
        posts=[
            Post(
                post_id=1,
                user_id=1,
                title="テスト",
                slug="test",
                thumbnail_url=None,
                status=PostStatus.PUBLISHED,
                published_at=datetime(2025, 1, 3),
                created_at=datetime(2025, 1, 1),
                updated_at=datetime(2025, 1, 2),
            )
        ],
    )

    response = client.get("/admin/posts", headers=auth_headers)

    assert response.status_code == 200

    post = response.json()["posts"][0]
    assert post["published_at"] == "2025-01-03T00:00:00"
    assert post["created_at"] == "2025-01-01T00:00:00"
    assert post["updated_at"] == "2025-01-02T00:00:00"
    assert "publishedAt" not in post
    assert "createdAt" not in post
    assert "updatedAt" not in post


# 最大文字数バリデーションエラー
def test_validation_error_max_length(client, auth_headers):
    response = client.get(
        "/admin/posts",
        headers=auth_headers,
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
def test_validation_error_min_length(client, auth_headers):
    response = client.get(
        "/admin/posts",
        headers=auth_headers,
        params={"offset": Constant.MIN_OFFSET - 1, "limit": Constant.MIN_LIMIT - 1},
    )

    assert response.status_code == 400

    data = response.json()
    messages = [item["message"] for item in data["details"]]

    assert data["error"] == ErrorCode.VALIDATION_ERROR
    assert ErrorMessage.MIN_OFFSET in messages
    assert ErrorMessage.MIN_LIMIT in messages
