from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.user import User


class UserRepository:

    def __init__(self, db: Session) -> None:
        self.db = db

    def find_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        return self.db.execute(stmt).scalars().first()

    def find_by_id(self, user_id: int) -> User | None:
        stmt = select(User).where(User.user_id == user_id)
        return self.db.execute(stmt).scalars().first()

    def update_account_name(self, user: User, account_name: str) -> User:
        user.account_name = account_name
        return user

    def update_password(self, user: User, hashed_password: str) -> User:
        user.password = hashed_password
        return user

    def update_email(self, user: User, new_email: str) -> User:
        user.username = new_email
        return user

    def exists_by_username(self, username: str) -> bool:
        stmt = select(User.user_id).where(User.username == username)
        return self.db.execute(stmt).first() is not None
