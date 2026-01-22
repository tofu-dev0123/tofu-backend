from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pydantic import Field
import os
from urllib.parse import urlparse


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

    # ===== クッキー設定 =====
    COOKIE_SECURE: bool = Field(True, description="HTTPS接続時のみクッキーを送信するか")
    COOKIE_HTTP_ONLY: bool = Field(True, description="JavaScriptからアクセス不可にするか")
    COOKIE_SAME_SITE: str = Field("lax", description="SameSite属性（lax/strict/none）")

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
            return self.MYSQLHOST
        return self.DB_HOST or "localhost"

    @property
    def db_port(self) -> int:
        if not self.is_local:
            return self.MYSQLPORT
        return self.DB_PORT or 3306

    @property
    def db_user(self) -> str:
        if not self.is_local:
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

    # ===== クッキー設定 共通取得 =====
    @property
    def cookie_domain(self) -> str | None:
        """
        クッキーのドメインを取得（ローカル環境ではNone）
        CORS_ALLOW_ORIGINSから自動的にドメインを抽出し、
        サブドメイン対応のため、先頭にドットを付与（例: tofubase.com -> .tofubase.com）
        """
        if self.is_local:
            return None
        
        if not self.CORS_ALLOW_ORIGINS:
            return None
        
        # CORS_ALLOW_ORIGINSからドメインを抽出
        domains = []
        for origin in self.CORS_ALLOW_ORIGINS:
            try:
                parsed = urlparse(origin)
                domain = parsed.netloc or parsed.path
                # ポート番号を除去
                if ":" in domain:
                    domain = domain.split(":")[0]
                if domain:
                    domains.append(domain)
            except Exception:
                # URLの解析に失敗した場合はスキップ
                continue
        
        if not domains:
            return None
        
        # 共通の親ドメインを抽出
        # 例: ["tofubase.com", "dev.tofubase.com"] -> "tofubase.com"
        if len(domains) == 1:
            base_domain = domains[0]
        else:
            # 複数のドメインがある場合、共通の親ドメインを抽出
            # ドメインを分割して、最も長い共通部分を探す
            domain_parts = [d.split(".") for d in domains]
            # 最短のドメイン部分数を取得
            min_parts = min(len(parts) for parts in domain_parts)
            
            # 末尾から共通部分を探す
            common_parts = []
            for i in range(1, min_parts + 1):
                suffixes = [tuple(parts[-i:]) for parts in domain_parts]
                if len(set(suffixes)) == 1:
                    common_parts = list(suffixes[0])
                else:
                    break
            
            if common_parts:
                base_domain = ".".join(common_parts)
            else:
                # 共通部分が見つからない場合は最初のドメインを使用
                base_domain = domains[0]
        
        # 既にドットで始まっている場合はそのまま返す
        if base_domain.startswith("."):
            return base_domain
        
        # ドットで始まっていない場合は先頭にドットを追加
        # これにより、tofubase.comとdev.tofubase.comの両方で動作する
        return f".{base_domain}"

    @property
    def cookie_secure(self) -> bool:
        """クッキーのSecure属性（本番環境ではTrue）"""
        if self.is_local:
            return False
        return self.COOKIE_SECURE


settings = Settings()
