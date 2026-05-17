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
