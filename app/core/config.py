from pydantic_settings import BaseSettings
from typing import Optional
from pydantic import Field
import os


class Settings(BaseSettings):
    # ===== 環境 =====
    APP_ENV: str = Field("local")
    
    # ===== Railway MySQL =====
    MYSQLHOST: Optional[str] = None
    MYSQLPORT: Optional[int] = None
    MYSQLUSER: Optional[str] = None
    MYSQLPASSWORD: Optional[str] = None
    MYSQLDATABASE: Optional[str] = None

    # ===== Local / Develop MySQL =====
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[int] = 3306
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_NAME: Optional[str] = None

    # ===== JWT =====
    SECRET_KEY: str
    ALGORITHM: str = os.getenv("ALGORITHM")
    
    # ===== 環境判別 =====
    @property
    def is_local(self) -> bool:
        return self.APP_ENV == "local"

    @property
    def is_develop(self) -> bool:
        return self.APP_ENV == "develop"

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"
    
    # ===== DB 共通取得 =====
    @property
    def db_host(self) -> str:
        if self.is_production:
            return self.MYSQLHOST
        return self.DB_HOST or "localhost"
    
    @property
    def db_port(self) -> int:
        if self.is_production:
            return self.MYSQLPORT or 3306
        return self.DB_PORT or 3306

    @property
    def db_user(self) -> str:
        if self.is_production:
            return self.MYSQLUSER
        return self.DB_USER or "root"

    @property
    def db_password(self) -> str:
        if self.is_production:
            return self.MYSQLPASSWORD or ""
        return self.DB_PASSWORD or ""

    @property
    def db_name(self) -> str:
        if self.is_production:
            return self.MYSQLDATABASE
        return self.DB_NAME or "blog_db"
    
    # ===== DB URL =====
    @property
    def database_url(self) -> str:
        password = (
            self.db_password.replace("%", "%25")
            .replace("@", "%40")
        )

        return (
            f"mysql+pymysql://{self.db_user}:{password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
            "?charset=utf8mb4"
        )

    
    @property
    def secret_key(self) -> str:
        """JWT秘密鍵を取得"""
        key = self.SECRET_KEY or os.getenv("SECRET_KEY")
        if not key:
            raise ValueError("SECRET_KEY環境変数が設定されていません")
        return key

    # データベースURLを構築
    @property
    def database_url(self) -> str:
        # パスワードに特殊文字が含まれる場合のエスケープ処理
        password = self.db_password.replace("%", "%25").replace("@", "%40")
        url = f"mysql+pymysql://{self.db_user}:{password}@{self.db_host}:{self.db_port}/{self.db_name}?charset=utf8mb4"

        return url

    class Config:
        # ENV_FILE=.env.local / .env.develop を起動時に切り替える
        env_file = os.getenv("ENV_FILE", ".env.local")
        case_sensitive = True


settings = Settings()
