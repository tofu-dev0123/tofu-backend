import pytest
from unittest.mock import patch
from datetime import datetime
from app.common.errorcode import ErrorCode
from app.common.message import ErrorMessage
from app.common.constant import Constant
from app.schemas.post import (
    PostsPublishAtResponse,
    PostPublishAt,
    PostPublishAtResponse,
    PostSlugsResponse,
)
from app.schemas.tag import Tag


# 正常系: 公開記事スラグ一覧の取得成功
@patch("app.services.public.post_service.PublicPostService.get_slugs")
def test_get_slugs_success(mock_get_slugs, client):
    mock_get_slugs.return_value = PostSlugsResponse(
        slugs=["first-post", "second-post", "hello-world"]
    )

    response = client.get("/posts/slugs")

    assert response.status_code == 200
    data = response.json()
    assert data["slugs"] == ["first-post", "second-post", "hello-world"]
    mock_get_slugs.assert_called_once_with()


# 正常系: 公開記事が0件の場合は空配列を返す
@patch("app.services.public.post_service.PublicPostService.get_slugs")
def test_get_slugs_empty(mock_get_slugs, client):
    mock_get_slugs.return_value = PostSlugsResponse(slugs=[])

    response = client.get("/posts/slugs")

    assert response.status_code == 200
    assert response.json()["slugs"] == []
    mock_get_slugs.assert_called_once_with()


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
                tags=[],
            ),
            PostPublishAt(
                post_id=2,
                title="テストタイトル2",
                slug="test-slug-2",
                thumbnail_url=None,
                published_at=datetime(2025, 1, 2, 12, 0, 0),
                tags=[],
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
                tags=[],
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
                tags=[],
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


# 正常系: 公開記事詳細の取得成功（タグあり）
@patch("app.services.public.post_service.PublicPostService.get_post")
def test_get_post_success_with_tags(mock_get_post, client):
    mock_response = PostPublishAtResponse(
        post_id=1,
        title="テストタイトル",
        slug="test-slug",
        content_html="<p>テスト本文</p>",
        thumbnail_url="https://example.com/thumb.png",
        tags=[
            Tag(tag_id=1, name="Python", slug="python"),
            Tag(tag_id=2, name="FastAPI", slug="fastapi"),
        ],
        published_at=datetime(2025, 1, 1, 12, 0, 0),
    )
    mock_get_post.return_value = mock_response

    response = client.get("/posts/test-slug")

    assert response.status_code == 200
    data = response.json()
    assert data["post_id"] == 1
    assert data["title"] == "テストタイトル"
    assert data["slug"] == "test-slug"
    assert data["content_html"] == "<p>テスト本文</p>"
    assert data["thumbnail_url"] == "https://example.com/thumb.png"
    assert len(data["tags"]) == 2
    assert data["tags"][0]["tag_id"] == 1
    assert data["tags"][0]["name"] == "Python"
    assert data["tags"][0]["slug"] == "python"
    assert data["tags"][1]["tag_id"] == 2
    assert data["tags"][1]["name"] == "FastAPI"
    assert data["tags"][1]["slug"] == "fastapi"
    mock_get_post.assert_called_once_with("test-slug")


# 正常系: 公開記事詳細の取得成功（タグなし）
@patch("app.services.public.post_service.PublicPostService.get_post")
def test_get_post_success_without_tags(mock_get_post, client):
    mock_response = PostPublishAtResponse(
        post_id=1,
        title="テストタイトル",
        slug="test-slug",
        content_html="<p>テスト本文</p>",
        thumbnail_url=None,
        tags=[],
        published_at=datetime(2025, 1, 1, 12, 0, 0),
    )
    mock_get_post.return_value = mock_response

    response = client.get("/posts/test-slug")

    assert response.status_code == 200
    data = response.json()
    assert data["post_id"] == 1
    assert data["title"] == "テストタイトル"
    assert data["slug"] == "test-slug"
    assert data["content_html"] == "<p>テスト本文</p>"
    assert data["thumbnail_url"] is None
    assert len(data["tags"]) == 0
    mock_get_post.assert_called_once_with("test-slug")


# 異常系: 記事が存在しない場合
@patch("app.services.public.post_service.PublicPostService.get_post")
def test_get_post_not_found(mock_get_post, client):
    from app.core.exceptions.handlers import ApplicationError

    mock_get_post.side_effect = ApplicationError(
        message=ErrorMessage.NOT_EXIST,
        code=ErrorCode.NOT_EXIST,
    )

    response = client.get("/posts/non-existent-slug")

    assert response.status_code == 400
    data = response.json()
    assert data["error"] == ErrorCode.NOT_EXIST
    assert data["message"] == ErrorMessage.NOT_EXIST
    mock_get_post.assert_called_once_with("non-existent-slug")
