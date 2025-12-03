from datetime import datetime, timedelta
from typing import List
import bcrypt
from jose import jwt
from app.core.config import settings
from app.schemas.auth import ErrorDetail


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
        "exp": expire  # 有効期限
    }
    
    # JWTトークンを生成
    token = jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.ALGORITHM
    )
    
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
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


class ValidationError(Exception):
    """バリデーションエラー"""
    def __init__(self, message: str, details: List[ErrorDetail]):
        self.message = message
        self.details = details
        super().__init__(self.message)


class LoginFailError(Exception):
    """ログイン失敗エラー（ユーザー不存在、パスワード不一致）"""
    def __init__(self, message: str = "ユーザー名またはパスワードが間違っています"):
        self.message = message
        super().__init__(self.message)

