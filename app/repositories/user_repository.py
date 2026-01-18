from sqlalchemy.orm import Session
from app.models.user import User


class UserRepository:

    def __init__(self, db: Session):
        self.db = db

    def find_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username).first()

    def find_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.user_id == user_id).first()

    def update_account_name(self, user: User, account_name: str) -> User:
        user.account_name = account_name
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_password(self, user: User, hashed_password: str) -> User:
        user.password = hashed_password
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_email(self, user: User, new_email: str) -> User:
        user.username = new_email
        self.db.commit()
        self.db.refresh(user)
        return user

    def exists_by_username(self, username: str) -> bool:
        return (
            self.db.query(User).filter(User.username == username).first() is not None
        )
