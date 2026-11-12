import logging
from unittest.mock import patch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.common.errorcode import ErrorCode
from app.common.message import ErrorMessage
from app.core.exceptions.s3_exceptions import S3FileDeleteError


# 予期しない例外: 500 の ErrorResponse を返し、ERROR ログは 1 回だけ出る
def test_unexpected_error_internal_server_error(app: FastAPI, caplog):
    client = TestClient(app, raise_server_exceptions=False)

    with patch(
        "app.services.auth_service.AuthService.login", side_effect=RuntimeError("boom")
    ), caplog.at_level(logging.INFO):
        response = client.post(
            "/admin/auth/login",
            json={"username": "admin@example.com", "password": "correctpass"},
        )

    assert response.status_code == 500
    assert response.json() == {
        "message": ErrorMessage.INTERNAL_SERVER_ERROR,
        "error": ErrorCode.INTERNAL_SERVER_ERROR,
        "details": [],
    }

    error_records = [
        r for r in caplog.records if r.name.startswith("app") and r.levelno >= logging.ERROR
    ]
    assert len(error_records) == 1
    assert error_records[0].name == "app.request"
    assert error_records[0].getMessage() == "request failed"
    assert error_records[0].exc_info is not None


# 存在しないパス: 404 の ErrorResponse
def test_http_error_not_found(client):
    response = client.get("/not-exist-path")

    assert response.status_code == 404
    assert response.json() == {
        "message": "Not Found",
        "error": ErrorCode.NOT_FOUND,
        "details": [],
    }


# 許可されないメソッド: 405 の ErrorResponse（Allow ヘッダは維持）
def test_http_error_method_not_allowed(client):
    response = client.get("/admin/auth/login")

    assert response.status_code == 405
    assert response.json() == {
        "message": "Method Not Allowed",
        "error": ErrorCode.METHOD_NOT_ALLOWED,
        "details": [],
    }
    assert "POST" in response.headers["allow"]


# S3 削除失敗: 400 の ErrorResponse
def test_s3_delete_error(client, override_current_user):
    with patch(
        "app.services.post_service.PostService.delete_all",
        side_effect=S3FileDeleteError(),
    ):
        response = client.delete("/admin/posts/1")

    assert response.status_code == 400
    assert response.json() == {
        "message": ErrorMessage.S3_FILE_DELETE_ERROR,
        "error": ErrorCode.S3_ERROR,
        "details": [],
    }
