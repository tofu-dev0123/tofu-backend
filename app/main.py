from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import get_db
from app.api.router import api_router
from app.core.exceptions.handlers import register_exception_handlers
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


app = FastAPI()
register_exception_handlers(app)

# ルーターの登録
app.include_router(api_router)


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
