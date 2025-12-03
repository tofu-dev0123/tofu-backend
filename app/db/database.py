from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# エンジンの作成
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # 接続の有効性を確認
    pool_recycle=3600,  # 1時間で接続を再生成
    echo=False  # SQLクエリをログ出力する場合はTrue
)

# セッションの作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ベースクラス
Base = declarative_base()

# 依存性注入用の関数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()