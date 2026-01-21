from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.database import get_db
from app.api.router import api_router
from app.core.exceptions.handlers import register_exception_handlers
from app.core.middleware import OriginCheckMiddleware
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


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

# 本番環境でのオリジンチェックミドルウェア
# CORSミドルウェアの後に追加（リクエストの順序が重要）
app.add_middleware(OriginCheckMiddleware)

# ルーターの登録
app.include_router(api_router)
