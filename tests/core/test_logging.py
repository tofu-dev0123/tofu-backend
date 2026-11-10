import json
import logging
import sys
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.core.logging.context import RequestIdFilter, request_id_ctx
from app.core.logging.formatters import HumanFormatter, JsonFormatter
from app.core.logging.middleware import RequestLoggingMiddleware


def _record(msg: str = "hello", **extra: object) -> logging.LogRecord:
    record = logging.LogRecord(
        name="app.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg=msg,
        args=(),
        exc_info=None,
    )
    for key, value in extra.items():
        setattr(record, key, value)
    return record


# ==================== RequestIdFilter ====================


# contextvar の request_id を record に付与する
def test_request_id_filter_sets_request_id():
    token = request_id_ctx.set("req-1")
    try:
        record = _record()
        assert RequestIdFilter().filter(record) is True
        assert getattr(record, "request_id") == "req-1"
    finally:
        request_id_ctx.reset(token)


# リクエスト外では None を付与する
def test_request_id_filter_outside_request():
    record = _record()

    RequestIdFilter().filter(record)

    assert getattr(record, "request_id") is None


# ==================== JsonFormatter ====================


# 共通フィールドと extra の付帯フィールドを JSON に出力する
def test_json_formatter_fields():
    record = _record("hello", request_id="req-1", path="/posts", status_code=200)

    payload = json.loads(JsonFormatter().format(record))

    assert payload["level"] == "INFO"
    assert payload["logger"] == "app.test"
    assert payload["message"] == "hello"
    assert payload["request_id"] == "req-1"
    assert payload["path"] == "/posts"
    assert payload["status_code"] == 200
    assert payload["timestamp"].endswith("Z")
    assert "stack" not in payload


# 例外情報は stack フィールドに格納する
def test_json_formatter_exception():
    try:
        raise ValueError("boom")
    except ValueError:
        record = _record("failed")
        record.exc_info = sys.exc_info()

    payload = json.loads(JsonFormatter().format(record))

    assert "ValueError: boom" in payload["stack"]


# ==================== HumanFormatter ====================


def test_human_formatter_with_request_id():
    output = HumanFormatter().format(_record("hello", request_id="req-1"))

    assert "INFO" in output
    assert "app.test" in output
    assert "[req-1]" in output
    assert output.endswith("hello")


# request_id 未設定時は "-" を表示する
def test_human_formatter_without_request_id():
    output = HumanFormatter().format(_record("hello"))

    assert "[-]" in output


# ==================== RequestLoggingMiddleware ====================


def _client() -> TestClient:
    app = FastAPI()
    app.add_middleware(RequestLoggingMiddleware)

    @app.get("/ping")
    def ping() -> dict[str, str | None]:
        return {"request_id": request_id_ctx.get()}

    return TestClient(app)


# X-Request-ID があれば踏襲し、レスポンスヘッダとエンドポイント内の contextvar に反映する
def test_middleware_uses_incoming_request_id():
    response = _client().get("/ping", headers={"X-Request-ID": "incoming-id"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "incoming-id"
    assert response.json()["request_id"] == "incoming-id"


# X-Request-ID がなければ採番する
def test_middleware_generates_request_id():
    response = _client().get("/ping")

    request_id = response.headers["X-Request-ID"]
    assert len(request_id) == 32
    assert response.json()["request_id"] == request_id


# 完了時にアクセスログを 1 行出す（リクエスト後は contextvar を戻す）
def test_middleware_access_log(caplog):
    with caplog.at_level(logging.INFO, logger="app.request"):
        _client().get("/ping")

    records = [r for r in caplog.records if r.name == "app.request"]
    assert len(records) == 1
    record = records[0]
    assert record.getMessage() == "request completed"
    assert getattr(record, "method") == "GET"
    assert getattr(record, "path") == "/ping"
    assert getattr(record, "status_code") == 200
    assert request_id_ctx.get() is None
