from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import get_db
from app.api.admin import auth

app = FastAPI()

# ルーターの登録
app.include_router(auth.router, prefix="/admin/auth", tags=["admin"])

@app.get("/")
def health_check():
    return {"message": "Hello Railway!"}

@app.get("/db-test")
def test_db(db: Session = Depends(get_db)):
    # データベース接続のテスト
    try:
        result = db.execute(text("SELECT 1"))
        return {"status": "connected", "message": "データベース接続成功"}
    except Exception as e:
        return {"status": "error", "message": str(e)}