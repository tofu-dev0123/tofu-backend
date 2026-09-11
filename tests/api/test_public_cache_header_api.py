from unittest.mock import patch
from datetime import datetime
from app.common.constant import Constant
from app.common.errorcode import ErrorCode
from app.common.message import ErrorMessage
from app.schemas.post import (
    PostPublishAtResponse,
    PostSlugsResponse,
)


# 正常系: 公開記事詳細に CDN キャッシュ用ヘッダが付与される
@patch("app.services.public.post_service.PublicPostService.get_post")
def test_public_post_detail_cache_header(mock_get_post, client):
    mock_get_post.return_value = PostPublishAtResponse(
        post_id=1,
        title="テストタイトル",
        slug="test-slug",
        content_html="<p>本文</p>",
        thumbnail_url=None,
        tags=[],
        published_at=datetime(2025, 1, 1, 12, 0, 0),
    )

    response = client.get("/posts/test-slug")

    assert response.status_code == 200
    assert response.headers["Cache-Control"] == Constant.PUBLIC_CACHE_CONTROL


# 正常系: 公開記事スラグ一覧にも CDN キャッシュ用ヘッダが付与される
@patch("app.services.public.post_service.PublicPostService.get_slugs")
def test_public_slugs_cache_header(mock_get_slugs, client):
    mock_get_slugs.return_value = PostSlugsResponse(slugs=["test-slug"])

    response = client.get("/posts/slugs")

    assert response.status_code == 200
    assert response.headers["Cache-Control"] == Constant.PUBLIC_CACHE_CONTROL


# 異常系: エラーレスポンスにはキャッシュ用ヘッダを付けない
@patch("app.services.public.post_service.PublicPostService.get_post")
def test_public_post_detail_error_has_no_cache_header(mock_get_post, client):
    from app.core.exceptions.handlers import ApplicationError

    mock_get_post.side_effect = ApplicationError(
        message=ErrorMessage.NOT_EXIST,
        code=ErrorCode.NOT_EXIST,
    )

    response = client.get("/posts/non-existent-slug")

    assert response.status_code == 400
    assert "Cache-Control" not in response.headers


# 異常系: 管理APIにはキャッシュ用ヘッダを付けない
def test_admin_api_has_no_cache_header(client):
    response = client.post("/admin/auth/logout")

    assert "Cache-Control" not in response.headers
