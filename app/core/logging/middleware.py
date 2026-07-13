import logging
import time
import uuid

from app.core.logging.context import request_id_ctx

logger = logging.getLogger("app.request")

# ヘッダ名は ASGI scope 上バイト列で扱う (小文字で正規化されている)
_REQUEST_ID_HEADER = b"x-request-id"


class RequestLoggingMiddleware:
    """リクエストごとに request_id を採番し、完了時にアクセスログを 1 行出す。

    BaseHTTPMiddleware は別タスクで dispatch されるため contextvar が
    エンドポイントへ伝播しない。それを避けるため純粋な ASGI ミドルウェアで実装する。

    - X-Request-ID があれば踏襲、なければ uuid4 を採番する (Cloudflare 等との相関用)。
    - 採番した ID はレスポンスヘッダ X-Request-ID にも返す。
    - 秘匿情報を避けるため body / query string / ヘッダはログに含めない。
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers") or [])
        incoming = headers.get(_REQUEST_ID_HEADER)
        request_id = incoming.decode("latin-1") if incoming else uuid.uuid4().hex
        token = request_id_ctx.set(request_id)

        start = time.perf_counter()
        status_code = 500

        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
                message_headers = message.setdefault("headers", [])
                message_headers.append((_REQUEST_ID_HEADER, request_id.encode("latin-1")))
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception:
            duration_ms = round((time.perf_counter() - start) * 1000, 1)
            logger.exception(
                "request failed",
                extra={
                    "method": scope.get("method"),
                    "path": scope.get("path"),
                    "duration_ms": duration_ms,
                },
            )
            raise
        else:
            duration_ms = round((time.perf_counter() - start) * 1000, 1)
            logger.info(
                "request completed",
                extra={
                    "method": scope.get("method"),
                    "path": scope.get("path"),
                    "status_code": status_code,
                    "duration_ms": duration_ms,
                },
            )
        finally:
            request_id_ctx.reset(token)
