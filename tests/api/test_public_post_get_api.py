import pytest
from unittest.mock import patch
from datetime import datetime
from app.common.errorcode import ErrorCode
from app.common.message import ErrorMessage
from app.common.constant import Constant
from app.schemas.post import PostsPublishAtResponse, PostPublishAt


# 正常系: 公開記事一覧の取得成功（page=1, keywordなし）
@patch("app.services.public.post_service.PublicPostService.get_posts")
def test_get_posts_success(mock_get_posts, client):
    mock_response = PostsPublishAtResponse(
        total_count=2,
        total_pages=1,
        page=1,
        limit=Constant.PUBLIC_POST_LIMIT,
        posts=[
            PostPublishAt(
                post_id=1,
                title="テストタイトル1",
                slug="test-slug-1",
                thumbnail_url="https://example.com/thumb1.png",
                published_at=datetime(2025, 1, 1, 12, 0, 0),
            ),
            PostPublishAt(
                post_id=2,
                title="テストタイトル2",
                slug="test-slug-2",
                thumbnail_url=None,
                published_at=datetime(2025, 1, 2, 12, 0, 0),
            ),
        ],
    )
    mock_get_posts.return_value = mock_response

    response = client.get("/posts/")

    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] == 2
    assert data["total_pages"] == 1
    assert data["page"] == 1
    assert data["limit"] == Constant.PUBLIC_POST_LIMIT
    assert len(data["posts"]) == 2
    assert data["posts"][0]["post_id"] == 1
    assert data["posts"][0]["title"] == "テストタイトル1"
    assert data["posts"][1]["post_id"] == 2
    mock_get_posts.assert_called_once_with(1, None)


# 正常系: キーワード検索での取得成功
@patch("app.services.public.post_service.PublicPostService.get_posts")
def test_get_posts_with_keyword_success(mock_get_posts, client):
    mock_response = PostsPublishAtResponse(
        total_count=1,
        total_pages=1,
        page=1,
        limit=Constant.PUBLIC_POST_LIMIT,
        posts=[
            PostPublishAt(
                post_id=1,
                title="Python記事",
                slug="python-post",
                thumbnail_url=None,
                published_at=datetime(2025, 1, 1, 12, 0, 0),
            ),
        ],
    )
    mock_get_posts.return_value = mock_response

    response = client.get("/posts/", params={"keyword": "Python"})

    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] == 1
    assert len(data["posts"]) == 1
    assert data["posts"][0]["title"] == "Python記事"
    mock_get_posts.assert_called_once_with(1, "Python")


# 正常系: ページネーション（page=2）
@patch("app.services.public.post_service.PublicPostService.get_posts")
def test_get_posts_pagination_success(mock_get_posts, client):
    mock_response = PostsPublishAtResponse(
        total_count=25,
        total_pages=3,
        page=2,
        limit=Constant.PUBLIC_POST_LIMIT,
        posts=[
            PostPublishAt(
                post_id=11,
                title="テストタイトル11",
                slug="test-slug-11",
                thumbnail_url=None,
                published_at=datetime(2025, 1, 11, 12, 0, 0),
            ),
        ],
    )
    mock_get_posts.return_value = mock_response

    response = client.get("/posts/", params={"page": 2})

    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] == 25
    assert data["total_pages"] == 3
    assert data["page"] == 2
    mock_get_posts.assert_called_once_with(2, None)


# バリデーションエラー: page < 1
def test_validation_error_page_min(client):
    response = client.get("/posts/", params={"page": 0})

    assert response.status_code == 400

    data = response.json()
    messages = [item["message"] for item in data["details"]]

    assert data["error"] == ErrorCode.VALIDATION_ERROR
    assert ErrorMessage.MIN_PAGE in messages


# バリデーションエラー: keyword が max_length 超過（1000文字超）
def test_validation_error_keyword_max_length(client):
    long_keyword = "a" * (Constant.MAX_KEYWORD_LENGTH + 1)
    response = client.get("/posts/", params={"keyword": long_keyword})

    assert response.status_code == 400

    data = response.json()
    messages = [item["message"] for item in data["details"]]

    assert data["error"] == ErrorCode.VALIDATION_ERROR
    assert ErrorMessage.KEYWORD_MAX_LENGTH in messages

