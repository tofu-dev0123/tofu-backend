import json
import logging
from datetime import datetime, timezone

# 標準 LogRecord が持つ属性 + 独自注入分。
# これら以外の record 属性 (logger.xxx(..., extra={...}) で渡された値) を
# 付帯フィールドとして JSON に展開する。
_RESERVED_ATTRS = frozenset(
    {
        "name",
        "msg",
        "args",
        "levelname",
        "levelno",
        "pathname",
        "filename",
        "module",
        "exc_info",
        "exc_text",
        "stack_info",
        "lineno",
        "funcName",
        "created",
        "msecs",
        "relativeCreated",
        "thread",
        "threadName",
        "processName",
        "process",
        "taskName",
        "message",
        "asctime",
        "request_id",
    }
)


def _format_timestamp(record: logging.LogRecord) -> str:
    dt = datetime.fromtimestamp(record.created, tz=timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{int(record.msecs):03d}Z"


class JsonFormatter(logging.Formatter):
    """構造化ログ (JSON) 用フォーマッタ。local 以外の環境で使用する。"""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict = {
            "timestamp": _format_timestamp(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", None),
        }

        # extra= で渡された付帯フィールド (method / path / status_code / duration_ms 等)
        for key, value in record.__dict__.items():
            if key not in _RESERVED_ATTRS and not key.startswith("_"):
                payload[key] = value

        if record.exc_info:
            payload["stack"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False, default=str)


class HumanFormatter(logging.Formatter):
    """人間可読フォーマッタ。local 環境で使用する。"""

    def __init__(self) -> None:
        super().__init__(
            fmt="%(asctime)s %(levelname)-8s %(name)s [%(request_id)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def format(self, record: logging.LogRecord) -> str:
        # request_id 未設定時は "-" を表示する
        if not getattr(record, "request_id", None):
            record.request_id = "-"
        return super().format(record)
