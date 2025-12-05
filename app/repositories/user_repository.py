from sqlalchemy.orm import Session
from app.models.user import User

def find_by_username(db: Session, username: str) -> User | None:
  return db.query(User).filter(User.username == username).first()