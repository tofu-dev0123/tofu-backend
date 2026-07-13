from unittest.mock import patch
from app.common.errorcode import ErrorCode
from app.common.message import Message, ErrorMessage
from app.schemas.timeline import Timeline, TimelineListResponse
from app.core.exceptions.handlers import ApplicationError


# 正常系: 年表一覧取得
@patch("app.services.timeline_service.TimelineService.get_timelines")
def test_get_timelines_success(mock_get, client, valid_token):
    mock_get.return_value = TimelineListResponse(
        timelines=[
            Timeline(timeline_id=1, year=2026, title="見出し", body="本文", sort_order=0),
        ]
    )

    response = client.get(
        "/admin/timelines", headers={"Authorization": f"Bearer {valid_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["timelines"]) == 1
    assert data["timelines"][0]["year"] == 2026


# 異常系: トークンなし
def test_get_timelines_no_token(client):
    response = client.get("/admin/timelines")
    assert response.status_code == 401


# 正常系: 年表作成
@patch("app.services.timeline_service.TimelineService.create_timeline")
def test_create_timeline_success(mock_create, client, valid_token):
    mock_create.return_value = 10

    req = {"year": 2026, "title": "t", "body": "b", "sort_order": 1}
    response = client.post(
        "/admin/timelines",
        headers={"Authorization": f"Bearer {valid_token}"},
        json=req,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == Message.TIMELINE_CREATE_SUCCESS
    assert data["timeline_id"] == 10


# バリデーションエラー: year 欠落
def test_create_timeline_validation_year_missing(client, valid_token):
    response = client.post(
        "/admin/timelines",
        headers={"Authorization": f"Bearer {valid_token}"},
        json={"title": "t"},
    )

    assert response.status_code == 400
    data = response.json()
    messages = [item["message"] for item in data["details"]]
    assert data["error"] == ErrorCode.VALIDATION_ERROR
    assert ErrorMessage.YEAR_REQUIRED in messages


# バリデーションエラー: year 範囲外
def test_create_timeline_validation_year_range(client, valid_token):
    response = client.post(
        "/admin/timelines",
        headers={"Authorization": f"Bearer {valid_token}"},
        json={"year": 1000},
    )

    assert response.status_code == 400
    data = response.json()
    messages = [item["message"] for item in data["details"]]
    assert ErrorMessage.YEAR_RANGE in messages


# 正常系: 年表更新
@patch("app.services.timeline_service.TimelineService.update_timeline")
def test_update_timeline_success(mock_update, client, valid_token):
    mock_update.return_value = None

    req = {"year": 2025, "title": "t", "body": "b", "sort_order": 0}
    response = client.put(
        "/admin/timelines/5",
        headers={"Authorization": f"Bearer {valid_token}"},
        json=req,
    )

    assert response.status_code == 200
    assert response.json()["message"] == Message.TIMELINE_UPDATE_SUCCESS


# 異常系: 更新対象が存在しない
@patch("app.services.timeline_service.TimelineService.update_timeline")
def test_update_timeline_not_found(mock_update, client, valid_token):
    mock_update.side_effect = ApplicationError(
        message=ErrorMessage.TIMELINE_NOT_EXIST, code=ErrorCode.NOT_EXIST
    )

    req = {"year": 2025, "sort_order": 0}
    response = client.put(
        "/admin/timelines/999",
        headers={"Authorization": f"Bearer {valid_token}"},
        json=req,
    )

    assert response.status_code == 400
    data = response.json()
    assert data["error"] == ErrorCode.NOT_EXIST
    assert data["message"] == ErrorMessage.TIMELINE_NOT_EXIST


# 正常系: 年表削除
@patch("app.services.timeline_service.TimelineService.delete_timeline")
def test_delete_timeline_success(mock_delete, client, valid_token):
    mock_delete.return_value = None

    response = client.delete(
        "/admin/timelines/3", headers={"Authorization": f"Bearer {valid_token}"}
    )

    assert response.status_code == 200
    assert response.json()["message"] == Message.TIMELINE_DELETE_SUCCESS
