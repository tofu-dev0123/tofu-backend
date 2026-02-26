from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pydantic import Field
import os


class Settings(BaseSettings):
    # ===== 環境 =====
    APP_ENV: str = Field("local")

    # ===== AWS =====
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_DEFAULT_REGION: str | None = None

    S3_BUCKET_NAME: str | None = None
    S3_ENDPOINT_URL: str | None = None
    CLOUDFRONT_DOMAIN: str | None = None

    # ===== Railway MySQL =====
    MYSQLHOST: Optional[str] = None
    MYSQLPORT: Optional[int] = None
    MYSQLUSER: Optional[str] = None
    MYSQLPASSWORD: Optional[str] = None
    MYSQLDATABASE: Optional[str] = None

    # ===== Local MySQL =====
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[int] = 3306
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_NAME: Optional[str] = None

    # ===== JWTキー =====
    SECRET_KEY: str
    ALGORITHM: str

    # ===== CORS設定 =====
    CORS_ALLOW_ORIGINS: list[str]

    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env.local"),
        case_sensitive=True,
        extra="forbid",
    )

    # ===== 環境判別 =====
    @property
    def is_local(self) -> bool:
        return self.APP_ENV == "local"

    # ===== DB 共通取得 =====
    @property
    def db_host(self) -> str:
        # local 以外 → Railway を使う
        if not self.is_local:
            assert self.MYSQLHOST is not None, "MYSQLHOST is not set"
            return self.MYSQLHOST
        return self.DB_HOST or "localhost"

    @property
    def db_port(self) -> int:
        if not self.is_local:
            assert self.MYSQLPORT is not None, "MYSQLPORT is not set"
            return self.MYSQLPORT
        return self.DB_PORT or 3306

    @property
    def db_user(self) -> str:
        if not self.is_local:
            assert self.MYSQLUSER is not None, "MYSQLUSER is not set"
            return self.MYSQLUSER
        return self.DB_USER or "root"

    @property
    def db_password(self) -> str:
        if not self.is_local:
            return self.MYSQLPASSWORD or ""
        return self.DB_PASSWORD or ""

    @property
    def db_name(self) -> str:
        if not self.is_local:
            assert self.MYSQLDATABASE is not None, "MYSQLDATABASE is not set"
            return self.MYSQLDATABASE
        return self.DB_NAME or "blog_db"

    # ===== DB URL =====
    @property
    def database_url(self) -> str:
        pwd = self.db_password.replace("%", "%25").replace("@", "%40")
        return (
            f"mysql+pymysql://{self.db_user}:{pwd}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
            "?charset=utf8mb4"
        )


settings = Settings()  # type: ignore[call-arg]
