from datetime import datetime, timedelta
import bcrypt
from jose import jwt, JWTError
from app.core.config import settings
from fastapi import Depends, Request
from app.models.user import User
from app.db.database import SessionLocal, get_db
from app.core.exceptions.auth_exceptions import AuthenticationError
from app.common.message import ErrorMessage


def create_access_token(user_id: int, username: str) -> str:
    """
    JWTトークンを生成する

    Args:
        user_id: ユーザーID
        username: ユーザー名

    Returns:
        JWTトークン文字列
    """
    # 有効期限を設定（現在時刻 + 3時間）
    expire = datetime.utcnow() + timedelta(hours=3)

    # ペイロード（クレーム）を設定
    payload = {
        "sub": str(user_id),  # ユーザーID
        "username": username,  # ユーザー名
        "exp": expire,  # 有効期限
    }

    # JWTトークンを生成
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

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


def hash_password(plain_password: str) -> str:
    """
    bcryptを使用してパスワードをハッシュ化する

    Args:
        plain_password: 平文パスワード

    Returns:
        ハッシュ化されたパスワード
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain_password.encode("utf-8"), salt).decode("utf-8")


def verify_token(token: str):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        raise AuthenticationError


def get_current_user(
    request: Request,
    db: SessionLocal = Depends(get_db),
) -> User:
    """
    クッキーまたはAuthorizationヘッダーから認証トークンを取得し、ユーザー情報を返す

    Args:
        request: FastAPIのRequestオブジェクト
        db: データベースセッション

    Returns:
        認証されたユーザー情報

    Raises:
        AuthenticationError: トークンが無効またはユーザーが存在しない場合
    """
    token = None
    
    # まずクッキーからトークンを取得
    token = request.cookies.get("auth_token")
    
    # クッキーにトークンがない場合、Authorizationヘッダーから取得
    if not token:
        authorization = request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            token = authorization.split("Bearer ")[1]
    
    if not token:
        raise AuthenticationError(ErrorMessage.TOKEN_REQUIRED)

    payload = verify_token(token)
    user_id = payload.get("sub")

    if not user_id:
        raise AuthenticationError

    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise AuthenticationError

    return user
