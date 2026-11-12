from fastapi import Response

from app.common.constant import Constant


def set_public_cache(response: Response) -> None:
    """公開 API のレスポンスに CDN キャッシュ用の Cache-Control を付与する。

    ブラウザには持たせず (max-age=0)、Cloudflare 側でのみ
    Constant.PUBLIC_CACHE_MAX_AGE 秒キャッシュさせる。
    例外発生時は例外ハンドラが別のレスポンスを生成するため、
    エラーレスポンスにはこのヘッダは付かない。
    """
    response.headers["Cache-Control"] = Constant.PUBLIC_CACHE_CONTROL
