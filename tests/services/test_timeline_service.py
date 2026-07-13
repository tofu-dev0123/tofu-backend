import pytest
from unittest.mock import MagicMock, Mock
from app.schemas.timeline import TimelinePostRequest, TimelinePutRequest
from app.core.exceptions.handlers import ApplicationError
from app.common.errorcode import ErrorCode
from app.common.message import ErrorMessage


# get_timelines: 正常系
def test_get_timelines_success(timeline_service):
    mock_timeline = Mock()
    mock_timeline.timeline_id = 1
    mock_timeline.year = 2026
    mock_timeline.title = "見出し"
    mock_timeline.body = "本文"
    mock_timeline.sort_order = 0

    timeline_service.timeline_repo = MagicMock()
    timeline_service.timeline_repo.find_all.return_value = [mock_timeline]

    result = timeline_service.get_timelines()

    assert len(result.timelines) == 1
    assert result.timelines[0].timeline_id == 1
    assert result.timelines[0].year == 2026


# create_timeline: 正常系
def test_create_timeline_success(timeline_service):
    timeline_service.timeline_repo = MagicMock()
    timeline_service.timeline_repo.create.return_value = 10
    timeline_service.db = MagicMock()

    req = TimelinePostRequest(year=2026, title="t", body="b", sort_order=1)

    result = timeline_service.create_timeline(req)

    assert result == 10
    timeline_service.db.commit.assert_called_once()


# update_timeline: 正常系
def test_update_timeline_success(timeline_service):
    timeline_service.timeline_repo = MagicMock()
    timeline_service.timeline_repo.exist_check.return_value = True
    timeline_service.db = MagicMock()

    req = TimelinePutRequest(year=2025, title="t2", body="b2", sort_order=2)

    result = timeline_service.update_timeline(5, req)

    assert result is None
    timeline_service.timeline_repo.update.assert_called_once_with(
        5, 2025, "t2", "b2", 2
    )
    timeline_service.db.commit.assert_called_once()


# update_timeline: 存在しない場合はロールバック
def test_update_timeline_not_exist(timeline_service):
    timeline_service.timeline_repo = MagicMock()
    timeline_service.timeline_repo.exist_check.return_value = False
    timeline_service.db = MagicMock()

    req = TimelinePutRequest(year=2025, title="t", body="b", sort_order=0)

    with pytest.raises(ApplicationError) as exc_info:
        timeline_service.update_timeline(5, req)

    assert exc_info.value.code == ErrorCode.NOT_EXIST
    assert exc_info.value.message == ErrorMessage.TIMELINE_NOT_EXIST
    timeline_service.db.rollback.assert_called_once()
    timeline_service.timeline_repo.update.assert_not_called()


# delete_timeline: 正常系
def test_delete_timeline_success(timeline_service):
    timeline_service.timeline_repo = MagicMock()
    timeline_service.timeline_repo.exist_check.return_value = True
    timeline_service.db = MagicMock()

    result = timeline_service.delete_timeline(3)

    assert result is None
    timeline_service.timeline_repo.delete.assert_called_once_with(3)
    timeline_service.db.commit.assert_called_once()


# delete_timeline: 存在しない場合はロールバック
def test_delete_timeline_not_exist(timeline_service):
    timeline_service.timeline_repo = MagicMock()
    timeline_service.timeline_repo.exist_check.return_value = False
    timeline_service.db = MagicMock()

    with pytest.raises(ApplicationError) as exc_info:
        timeline_service.delete_timeline(3)

    assert exc_info.value.code == ErrorCode.NOT_EXIST
    timeline_service.db.rollback.assert_called_once()
    timeline_service.timeline_repo.delete.assert_not_called()
