from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from app.core.config import settings
from app.db.database import get_db
from app.api.router import api_router
from app.core.exceptions.handlers import register_exception_handlers
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


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

# ルーターの登録
app.include_router(api_router)

# AWS Lambda 用 ASGI ハンドラ (Function URL / API Gateway 互換)
handler = Mangum(app, lifespan="off")
