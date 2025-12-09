from sqlalchemy.orm import Session
from app.models.user import User

class UserRepository:

    def __init__(self, db: Session):
        self.db = db

    def find_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username).first()
