from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pydantic import Field
import os
import logging

logger = logging.getLogger(__name__)


def _populate_env_from_ssm() -> None:
    """
    `<KEY>_SSM` 環境変数が設定されていれば、SSM Parameter Store から取得した値を
    `<KEY>` 環境変数として `os.environ` に注入する。Settings 初期化前に呼ぶこと。

    Lambda 実行時の secret 取得用 (DATABASE_URL, SECRET_KEY 等)。
    ローカル開発では `<KEY>_SSM` を設定しないので何もしない。
    """
    ssm_keys = ["DATABASE_URL", "SECRET_KEY"]
    targets = [k for k in ssm_keys if os.getenv(f"{k}_SSM") and not os.getenv(k)]
    if not targets:
        return

    import boto3  # 遅延 import (ローカル開発では呼ばれない)

    client = boto3.client("ssm")
    for key in targets:
        param_name = os.environ[f"{key}_SSM"]
        try:
            resp = client.get_parameter(Name=param_name, WithDecryption=True)
            os.environ[key] = resp["Parameter"]["Value"]
        except Exception as e:
            logger.error("Failed to fetch SSM parameter %s: %s", param_name, e)
            raise


_populate_env_from_ssm()


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

    # ===== Database (production: Neon などが提供する単一の接続文字列) =====
    DATABASE_URL: Optional[str] = None

    # ===== Local Database (Docker Postgres) =====
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[int] = 5432
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
        extra="ignore",
    )

    # ===== 環境判別 =====
    @property
    def is_local(self) -> bool:
        return self.APP_ENV == "local"

    # ===== DB URL =====
    @property
    def database_url(self) -> str:
        # 本番系: DATABASE_URL をそのまま使用 (Neon 等は単一接続文字列で提供される)
        if not self.is_local:
            assert self.DATABASE_URL is not None, "DATABASE_URL is not set"
            url = self.DATABASE_URL
            # Neon などが返す `postgres://` を SQLAlchemy/psycopg 用のスキームに正規化
            if url.startswith("postgres://"):
                url = "postgresql+psycopg://" + url[len("postgres://"):]
            elif url.startswith("postgresql://"):
                url = "postgresql+psycopg://" + url[len("postgresql://"):]
            return url

        # ローカル: DB_* から組み立て
        host = self.DB_HOST or "localhost"
        port = self.DB_PORT or 5432
        user = self.DB_USER or "postgres"
        pwd = (self.DB_PASSWORD or "").replace("%", "%25").replace("@", "%40")
        name = self.DB_NAME or "blog_db"
        return f"postgresql+psycopg://{user}:{pwd}@{host}:{port}/{name}"


settings = Settings()  # type: ignore[call-arg]
