import pytest
from unittest.mock import MagicMock, Mock
from app.schemas.profile import ProfilePutRequest
from app.core.exceptions.handlers import ApplicationError
from app.common.errorcode import ErrorCode
from app.common.message import ErrorMessage


# get_profile: 正常系
def test_get_profile_success(profile_service):
    mock_profile = Mock()
    mock_profile.headline = "Webエンジニア"
    mock_profile.bio = "自己紹介"
    mock_profile.site_description = "サイト説明"

    profile_service.profile_repo = MagicMock()
    profile_service.profile_repo.get.return_value = mock_profile

    result = profile_service.get_profile()

    assert result.headline == "Webエンジニア"
    assert result.bio == "自己紹介"
    assert result.site_description == "サイト説明"


# get_profile: レコードが存在しない場合
def test_get_profile_not_exist(profile_service):
    profile_service.profile_repo = MagicMock()
    profile_service.profile_repo.get.return_value = None

    with pytest.raises(ApplicationError) as exc_info:
        profile_service.get_profile()

    assert exc_info.value.code == ErrorCode.NOT_EXIST
    assert exc_info.value.message == ErrorMessage.PROFILE_NOT_EXIST


# update_profile: 正常系
def test_update_profile_success(profile_service):
    mock_profile = Mock()
    mock_profile.profile_id = 1

    profile_service.profile_repo = MagicMock()
    profile_service.profile_repo.get.return_value = mock_profile
    profile_service.db = MagicMock()

    req = ProfilePutRequest(
        headline="new headline", bio="new bio", site_description="new desc"
    )

    result = profile_service.update_profile(req)

    assert result is None
    profile_service.profile_repo.update.assert_called_once_with(
        1, "new headline", "new bio", "new desc"
    )
    profile_service.db.commit.assert_called_once()


# update_profile: レコードが存在しない場合はロールバック
def test_update_profile_not_exist(profile_service):
    profile_service.profile_repo = MagicMock()
    profile_service.profile_repo.get.return_value = None
    profile_service.db = MagicMock()

    req = ProfilePutRequest(headline="h", bio="b", site_description="s")

    with pytest.raises(ApplicationError) as exc_info:
        profile_service.update_profile(req)

    assert exc_info.value.code == ErrorCode.NOT_EXIST
    profile_service.db.rollback.assert_called_once()
    profile_service.profile_repo.update.assert_not_called()
