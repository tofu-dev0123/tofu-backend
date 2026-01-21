from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from urllib.parse import urlparse
from app.core.config import settings


class OriginCheckMiddleware(BaseHTTPMiddleware):
    """本番環境でフロントエンドのドメインからのリクエストのみを許可するミドルウェア"""

    def __init__(self, app):
        super().__init__(app)
        # CORS_ALLOW_ORIGINSからドメインを抽出
        self.allowed_domains = []
        for origin in settings.CORS_ALLOW_ORIGINS:
            parsed = urlparse(origin)
            domain = parsed.netloc.lower()
            # www.プレフィックスを除去したドメインも追加
            domain_without_www = domain.replace("www.", "")
            self.allowed_domains.append(domain)
            if domain != domain_without_www:
                self.allowed_domains.append(domain_without_www)

    async def dispatch(self, request: Request, call_next):
        # ローカル環境ではチェックをスキップ
        if settings.is_local:
            return await call_next(request)

        # OPTIONSリクエスト（CORSプリフライト）は除外
        if request.method == "OPTIONS":
            return await call_next(request)

        # Refererヘッダーを取得
        referer = request.headers.get("Referer") or request.headers.get("Referrer")

        if not referer:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Referer header is required"
            )

        # Refererからドメインを抽出
        try:
            parsed_referer = urlparse(referer)
            referer_domain = parsed_referer.netloc.lower()

            # www.プレフィックスを除去して比較
            domain_without_www = referer_domain.replace("www.", "")

            # 許可されたドメインかチェック
            is_allowed = False
            for allowed_domain in self.allowed_domains:
                allowed_without_www = allowed_domain.replace("www.", "")
                if referer_domain == allowed_domain or domain_without_www == allowed_without_www:
                    is_allowed = True
                    break

            if not is_allowed:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Requests must come from allowed domains: {', '.join(self.allowed_domains)}"
                )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid Referer header"
            )

        return await call_next(request)
