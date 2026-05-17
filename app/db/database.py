from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.base_class import Base

# エンジンの作成
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # 接続の有効性を確認
    pool_recycle=3600,  # 1時間で接続を再生成
    echo=False,  # SQLクエリをログ出力する場合はTrue
    connect_args={
        "connect_timeout": 10,
    },
)

# セッションの作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 依存性注入用の関数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
