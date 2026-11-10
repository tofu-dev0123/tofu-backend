import logging
from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.core.security import verify_password, hash_password
from app.services.transaction import transaction
from app.core.exceptions.account_exceptions import (
    PasswordMismatchError,
    EmailMismatchError,
    EmailAlreadyExistsError,
)

logger = logging.getLogger(__name__)


class AccountService:

    def __init__(
        self,
        db: Session,
        user_repo: UserRepository | None = None,
    ) -> None:
        self.db = db
        self.user_repo = user_repo or UserRepository(db)

    def update_account_name(self, user: User, account_name: str) -> User:
        """アカウント名を変更する"""
        with transaction(self.db):
            updated = self.user_repo.update_account_name(user, account_name)
        self.db.refresh(updated)
        logger.info("account name updated", extra={"user_id": user.user_id})
        return updated

    def change_password(
        self, user: User, current_password: str, new_password: str
    ) -> None:
        """パスワードを変更する"""
        # 現在のパスワードを検証
        if not verify_password(current_password, user.password):
            raise PasswordMismatchError()

        # 新しいパスワードをハッシュ化して更新
        hashed_password = hash_password(new_password)
        with transaction(self.db):
            self.user_repo.update_password(user, hashed_password)
        self.db.refresh(user)
        logger.info("password changed", extra={"user_id": user.user_id})

    def change_email(
        self, user: User, current_email: str, new_email: str, password: str
    ) -> User:
        """メールアドレスを変更する"""
        # 現在のメールアドレスを検証
        if user.username != current_email:
            raise EmailMismatchError()

        # パスワードを検証
        if not verify_password(password, user.password):
            raise PasswordMismatchError()

        # 新しいメールアドレスの重複チェック
        if self.user_repo.exists_by_username(new_email):
            raise EmailAlreadyExistsError()

        # メールアドレスを更新
        with transaction(self.db):
            updated = self.user_repo.update_email(user, new_email)
        self.db.refresh(updated)
        logger.info("email changed", extra={"user_id": user.user_id})
        return updated
