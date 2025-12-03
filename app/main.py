from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import get_db

app = FastAPI()

@app.get("/")
def health_check():
    return {"message": "Hello Railway!"}

@app.get("/db-test")
def test_db(db: Session = Depends(get_db)):
    # データベース接続のテスト
    try:
        result = db.execute(text("SELECT 1"))
        db.commit()
        return {"status": "connected", "message": "データベース接続成功"}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}