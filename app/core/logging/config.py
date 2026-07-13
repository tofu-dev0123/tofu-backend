import logging
import sys

from app.core.logging.context import RequestIdFilter
from app.core.logging.formatters import HumanFormatter, JsonFormatter


def setup_logging(*, is_local: bool) -> None:
    """アプリ全体のログ設定を初期化する。

    - 出力先は stdout (docker / Cloudflare 側で収集する前提)。
    - local は人間可読・DEBUG、それ以外は JSON・INFO。
    - RequestIdFilter で全ログに request_id を注入する。
    - uvicorn のロガーを root に集約し、フォーマットを統一する。
    """
    level = logging.DEBUG if is_local else logging.INFO
    formatter: logging.Formatter = HumanFormatter() if is_local else JsonFormatter()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.addFilter(RequestIdFilter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

    # uvicorn の各ロガーを root に集約し、独自ハンドラによる二重出力を防ぐ。
    for name in ("uvicorn", "uvicorn.error"):
        lg = logging.getLogger(name)
        lg.handlers.clear()
        lg.propagate = True

    # アクセスログはリクエストログミドルウェアが 1 行で出すため、
    # uvicorn.access の重複出力を無効化する。
    access_logger = logging.getLogger("uvicorn.access")
    access_logger.handlers.clear()
    access_logger.propagate = False
    access_logger.setLevel(logging.WARNING)
