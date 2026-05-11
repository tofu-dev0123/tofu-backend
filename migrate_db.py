#!/usr/bin/env python3
"""
データベースマイグレーション実行スクリプト
Docker起動時に自動的に実行されます
"""
import time
import sys
import os
import bcrypt
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.database import SessionLocal
from app.models import User
from alembic.config import Config
from alembic import command


def wait_for_database(max_retries=30, retry_interval=1):
    """データベースが準備できるまで待機"""
    print("Waiting for database to be ready...")

    engine = None
    for attempt in range(max_retries):
        try:
            engine = create_engine(
                settings.database_url,
                pool_pre_ping=True,
                connect_args={
                    "connect_timeout": 5,
                },
            )
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("Database is ready!")
            # 成功した場合はエンジンを破棄してから返す
            engine.dispose()
            return True
        except Exception as e:
            # エンジンを確実に破棄
            if engine is not None:
                engine.dispose()
                engine = None

            if attempt < max_retries - 1:
                print(
                    f"Database is unavailable (attempt {attempt + 1}/{max_retries}) - sleeping..."
                )
                time.sleep(retry_interval)
            else:
                print(
                    f"Failed to connect to database after {max_retries} attempts: {e}"
                )
                return False

    return False


def check_and_create_initial_migration():
    """初期マイグレーションファイルが存在しない場合は作成"""
    versions_dir = "alembic/versions"

    # versionsディレクトリ内にマイグレーションファイルがあるか確認
    if os.path.exists(versions_dir):
        migration_files = [
            f
            for f in os.listdir(versions_dir)
            if f.endswith(".py") and not f.startswith("__")
        ]
        if migration_files:
            print(f"Found {len(migration_files)} migration file(s)")
            return

    # 初期マイグレーションファイルが存在しない場合は作成
    print("No migration files found. Creating initial migration...")
    try:
        alembic_cfg = Config("alembic.ini")
        command.revision(alembic_cfg, autogenerate=True, message="Initial migration")
        print("Initial migration created successfully!")
    except Exception as e:
        print(f"Failed to create initial migration: {e}")
        # エラーが発生しても続行（手動で作成する必要がある場合がある）


def run_migrations():
    """Alembicマイグレーションを実行"""
    print("Running database migrations...")

    try:
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        print("Migrations completed successfully!")
        return True
    except Exception as e:
        print(f"Migration failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


def create_initial_data():
    """初期データを作成（adminユーザー）"""
    print("Creating initial data...")

    db: Session = SessionLocal()
    try:
        # adminユーザーが既に存在するか確認
        existing_user = (
            db.query(User).filter(User.username == "admin@example.com").first()
        )
        if existing_user:
            print("Admin user already exists, skipping initial data creation.")
            return

        # パスワードをハッシュ化
        password = "password"
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        # adminユーザーを作成
        admin_user = User(
            username="admin@example.com",
            password=hashed_password,
            account_name="testuser",
        )

        db.add(admin_user)
        db.commit()
        print("Initial data created successfully! (admin user)")

    except Exception as e:
        db.rollback()
        print(f"Failed to create initial data: {e}")
        import traceback

        traceback.print_exc()
        # 初期データ作成の失敗は致命的ではないので、続行
    finally:
        db.close()


# ---- migrate_db.py (修正版) ----

if __name__ == "__main__":
    if not wait_for_database():
        sys.exit(1)

    check_and_create_initial_migration()

    print("Running alembic upgrade...")
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

    print("Inserting seed data...")
    create_initial_data()
