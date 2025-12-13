import pytest
from unittest.mock import patch
from types import SimpleNamespace


# 正常系
@patch("app.services.post_service.PostService.get_summary")
def test_get_posts_success(mock_get_summary, client, valid_token):
    mock_get_summary.return_value = SimpleNamespace(
        _mapping={
            "total_count": 2,
            "published_count": 1,
            "draft_count": 1,
        }
    )

    response = client.get(
        "/admin/posts/summary",
        headers={"Authorization": f"Bearer {valid_token}"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["total_count"] == 2
    assert data["published_count"] == 1
    assert data["draft_count"] == 1
