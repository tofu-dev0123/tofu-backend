import contextvars
import logging

# リクエストごとに採番される相関 ID を保持する contextvar。
# ミドルウェアで set され、同一リクエスト内の全ログに注入される。
request_id_ctx: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "request_id", default=None
)


class RequestIdFilter(logging.Filter):
    """全 LogRecord に request_id 属性を付与するフィルタ。

    contextvar が未設定 (リクエスト外) の場合は None を設定する。
    """

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx.get()
        return True
