from unittest.mock import patch
from app.schemas.profile import ProfileResponse, AboutResponse
from app.schemas.timeline import Timeline


# 正常系: About ページ情報の取得（プロフィール＋年表）
@patch("app.services.public.about_service.PublicAboutService.get_about")
def test_get_about_success(mock_get_about, client):
    mock_get_about.return_value = AboutResponse(
        profile=ProfileResponse(
            headline="Webエンジニア", bio="自己紹介", site_description="サイト説明"
        ),
        timelines=[
            Timeline(timeline_id=1, year=2026, title="見出し", body="本文", sort_order=0),
            Timeline(timeline_id=2, year=2025, title=None, body=None, sort_order=1),
        ],
    )

    response = client.get("/about")

    assert response.status_code == 200
    data = response.json()
    assert data["profile"]["headline"] == "Webエンジニア"
    assert len(data["timelines"]) == 2
    assert data["timelines"][0]["year"] == 2026
    mock_get_about.assert_called_once_with()


# 正常系: 年表が空でも取得できる
@patch("app.services.public.about_service.PublicAboutService.get_about")
def test_get_about_empty_timelines(mock_get_about, client):
    mock_get_about.return_value = AboutResponse(
        profile=ProfileResponse(headline="", bio="", site_description=""),
        timelines=[],
    )

    response = client.get("/about")

    assert response.status_code == 200
    data = response.json()
    assert data["timelines"] == []
