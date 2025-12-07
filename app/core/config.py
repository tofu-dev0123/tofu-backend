from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # データベース設定（Railwayの環境変数とカスタム環境変数の両方に対応）
    # Railwayの標準環境変数名
    MYSQLHOST: Optional[str] = None
    MYSQLPORT: Optional[int] = None
    MYSQLUSER: Optional[str] = None
    MYSQLPASSWORD: Optional[str] = None
    MYSQLDATABASE: Optional[str] = None

    # カスタム環境変数名（開発環境用）
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[int] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_NAME: Optional[str] = None

    # JWT設定
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM")

    @property
    def db_host(self) -> str:
        """データベースホストを取得（Railway優先、次にカスタム、最後にデフォルト）"""
        # Railwayの環境変数を直接確認（Pydanticが読み取れない場合に備えて）
        return (
            self.MYSQLHOST
            or os.getenv("MYSQLHOST")
            or self.DB_HOST
            or os.getenv("DB_HOST")
            or os.getenv("MYSQL_HOST")
            or "localhost"
        )

    @property
    def db_port(self) -> int:
        """データベースポートを取得"""
        # ポート番号を取得（優先順位: MYSQLPORT > DB_PORT > 環境変数 > デフォルト）
        if self.MYSQLPORT is not None:
            return self.MYSQLPORT
        port_str = os.getenv("MYSQLPORT")
        if port_str:
            try:
                return int(port_str)
            except ValueError:
                pass
        if self.DB_PORT is not None:
            return self.DB_PORT
        port_str = os.getenv("DB_PORT") or os.getenv("MYSQL_PORT")
        if port_str:
            try:
                return int(port_str)
            except ValueError:
                pass
        return 3306

    @property
    def db_user(self) -> str:
        """データベースユーザーを取得"""
        return (
            self.MYSQLUSER
            or os.getenv("MYSQLUSER")
            or self.DB_USER
            or os.getenv("DB_USER")
            or os.getenv("MYSQL_USER")
            or "root"
        )

    @property
    def db_password(self) -> str:
        """データベースパスワードを取得"""
        return (
            self.MYSQLPASSWORD
            or os.getenv("MYSQLPASSWORD")
            or self.DB_PASSWORD
            or os.getenv("DB_PASSWORD")
            or os.getenv("MYSQL_PASSWORD")
            or ""
        )

    @property
    def db_name(self) -> str:
        """データベース名を取得"""
        return (
            self.MYSQLDATABASE
            or os.getenv("MYSQLDATABASE")
            or self.DB_NAME
            or os.getenv("DB_NAME")
            or os.getenv("MYSQL_DATABASE")
            or "blog_db"
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

        # デバッグ情報（本番環境でのトラブルシューティング用）
        # パスワードをマスクしたURLをログ出力
        masked_url = f"mysql+pymysql://{self.db_user}:***@{self.db_host}:{self.db_port}/{self.db_name}?charset=utf8mb4"
        print(f"[DEBUG] Database connection URL: {masked_url}")
        print(
            f"[DEBUG] DB_HOST: {self.db_host}, DB_PORT: {self.db_port}, DB_USER: {self.db_user}, DB_NAME: {self.db_name}"
        )

        return url

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
