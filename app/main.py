from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.router import api_router
from app.core.exceptions.handlers import register_exception_handlers
from app.core.logging.config import setup_logging
from app.core.logging.middleware import RequestLoggingMiddleware

setup_logging(is_local=settings.is_local)


if not settings.is_local:
    app = FastAPI(
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
else:
    app = FastAPI()

register_exception_handlers(app)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# リクエストログ / request_id 採番 (最外層に置き全処理を包む)
app.add_middleware(RequestLoggingMiddleware)

# ルーターの登録
app.include_router(api_router)
