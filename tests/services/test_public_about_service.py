import pytest
from unittest.mock import MagicMock, Mock
from app.services.public.about_service import PublicAboutService


@pytest.fixture
def about_service(mock_db):
    return PublicAboutService(
        mock_db, profile_repo=MagicMock(), timeline_repo=MagicMock()
    )


def _mock_timeline(timeline_id: int, year: int) -> Mock:
    timeline = Mock()
    timeline.timeline_id = timeline_id
    timeline.year = year
    timeline.title = f"title{timeline_id}"
    timeline.body = None
    timeline.sort_order = 0
    return timeline


# プロフィールと年表を返す
def test_get_about_success(about_service):
    profile = Mock()
    profile.headline = "headline"
    profile.bio = "bio"
    profile.site_description = "desc"
    about_service.profile_repo.get.return_value = profile
    about_service.timeline_repo.find_all.return_value = [
        _mock_timeline(1, 2024),
        _mock_timeline(2, 2023),
    ]

    result = about_service.get_about()

    assert result.profile.headline == "headline"
    assert result.profile.bio == "bio"
    assert result.profile.site_description == "desc"
    assert [t.timeline_id for t in result.timelines] == [1, 2]
    assert [t.year for t in result.timelines] == [2024, 2023]


# プロフィール未登録時は空文字のプロフィールを返す
def test_get_about_no_profile(about_service):
    about_service.profile_repo.get.return_value = None
    about_service.timeline_repo.find_all.return_value = []

    result = about_service.get_about()

    assert result.profile.headline == ""
    assert result.profile.bio == ""
    assert result.profile.site_description == ""
    assert result.timelines == []
