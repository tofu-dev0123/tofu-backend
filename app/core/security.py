from datetime import datetime, timedelta
import bcrypt
from jose import jwt, JWTError
from app.core.config import settings
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException, status, Depends
from app.schemas.errors import ErrorResponse
from app.models.user import User
from app.db.database import SessionLocal, get_db


security = HTTPBearer()


def create_access_token(user_id: int, username: str) -> str:
    """
    JWTトークンを生成する

    Args:
        user_id: ユーザーID
        username: ユーザー名

    Returns:
        JWTトークン文字列
    """
    # 有効期限を設定（現在時刻 + 60分）
    expire = datetime.utcnow() + timedelta(minutes=60)

    # ペイロード（クレーム）を設定
    payload = {
        "sub": str(user_id),  # ユーザーID
        "username": username,  # ユーザー名
        "exp": expire,  # 有効期限
    }

    # JWTトークンを生成
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.ALGORITHM)

    return token


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    bcryptを使用してパスワードを検証する

    Args:
        plain_password: 平文パスワード
        hashed_password: ハッシュ化されたパスワード

    Returns:
        検証結果（True: 一致、False: 不一致）
    """
    # bcryptでパスワードを検証
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def verify_token(token: str):
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorResponse(
                message="認証に失敗しました", error="AUTHENTICATION_ERROR", details=[]
            ).dict(),
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: SessionLocal = Depends(get_db),
):
    token = credentials.credentials
    payload = verify_token(token)
    user_id = payload.get("sub")

    if not user_id:
        raise AuthenticationError

    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise AuthenticationError

    return user


class LoginFailError(Exception):
    """ログイン失敗エラー（ユーザー不存在、パスワード不一致）"""

    def __init__(self, message: str = "ユーザー名またはパスワードが間違っています"):
        self.message = message
        super().__init__(self.message)


class AuthenticationError(Exception):
    """ログイン失敗エラー（ユーザー不存在、パスワード不一致）"""

    def __init__(self, message: str = "ユーザー名またはパスワードが間違っています"):
        self.message = message
        super().__init__(self.message)
