from sqlalchemy.orm import Session
from app.core.exceptions.auth_exceptions import LoginFailError
from app.repositories.user_repository import UserRepository
from app.core.security import create_access_token, verify_password

class AuthService:

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def login_service(self, username: str, password: str, db: Session) -> str:
        # ユーザー情報を取得
        user = self.user_repo.find_by_username(db, username)

        # ユーザーが存在しない場合
        if not user:
            raise LoginFailError()

        # 3. パスワードを照合
        if not verify_password(password, user.password):
            raise LoginFailError()

        # 4. JWTトークンを生成
        token = create_access_token(user.user_id, user.username)

        return token
