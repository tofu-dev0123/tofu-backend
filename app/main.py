from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db, engine, Base

# データベーステーブルを作成（開発環境用）
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def health_check():
    return {"message": "Hello Railway!"}

@app.get("/db-test")
def test_db(db: Session = Depends(get_db)):
    # データベース接続のテスト
    try:
        db.execute("SELECT 1")
        return {"status": "connected", "message": "データベース接続成功"}
    except Exception as e:
        return {"status": "error", "message": str(e)}