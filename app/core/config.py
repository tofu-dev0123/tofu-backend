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
    
    @property
    def db_host(self) -> str:
        """データベースホストを取得（Railway優先、次にカスタム、最後にデフォルト）"""
        return (
            self.MYSQLHOST or 
            self.DB_HOST or 
            os.getenv("MYSQL_HOST") or
            "localhost"
        )
    
    @property
    def db_port(self) -> int:
        """データベースポートを取得"""
        return (
            self.MYSQLPORT or 
            self.DB_PORT or 
            (int(os.getenv("MYSQL_PORT")) if os.getenv("MYSQL_PORT") else None) or
            3306
        )
    
    @property
    def db_user(self) -> str:
        """データベースユーザーを取得"""
        return (
            self.MYSQLUSER or 
            self.DB_USER or 
            os.getenv("MYSQL_USER") or
            "root"
        )
    
    @property
    def db_password(self) -> str:
        """データベースパスワードを取得"""
        return (
            self.MYSQLPASSWORD or 
            self.DB_PASSWORD or 
            os.getenv("MYSQL_PASSWORD") or
            ""
        )
    
    @property
    def db_name(self) -> str:
        """データベース名を取得"""
        return (
            self.MYSQLDATABASE or 
            self.DB_NAME or 
            os.getenv("MYSQL_DATABASE") or
            "blog_db"
        )
    
    # データベースURLを構築
    @property
    def database_url(self) -> str:
        # パスワードに特殊文字が含まれる場合のエスケープ処理
        password = self.db_password.replace("%", "%25").replace("@", "%40")
        return f"mysql+pymysql://{self.db_user}:{password}@{self.db_host}:{self.db_port}/{self.db_name}?charset=utf8mb4"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()