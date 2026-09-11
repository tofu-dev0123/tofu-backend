from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.base_class import Base

# エンジンの作成
engine = create_engine(
    settings.database_url,
    # pool_pre_ping は接続チェックアウトの度に SELECT 1 を投げるため、
    # DB が遠い (Neon: us-east-1) 現構成ではリクエスト毎に往復が 1 回増える。
    # レイテンシ削減のため無効化し、代わりに pool_recycle を短くして
    # 寝かせた接続を掴みにくくする。
    pool_pre_ping=False,
    pool_recycle=300,  # 5分で接続を再生成
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
