#!/usr/bin/env python3
"""
アプリケーション起動スクリプト
マイグレーションを実行してからアプリケーションを起動します
"""
import subprocess
import sys
import os

# if __name__ == "__main__":
#     # マイグレーションを実行
#     print("Running database migrations...")
#     result = subprocess.run([sys.executable, "migrate_db.py"], check=False)

#     if result.returncode != 0:
#         print("Migration failed, exiting...")
#         sys.exit(result.returncode)

#     # アプリケーションを起動
#     print("Starting application...")
#     subprocess.run(["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"])

def run_migration():
    print("Running database migrations...")
    result = subprocess.run([sys.executable, "migrate_db.py"])
    if result.returncode != 0:
        print("Migration failed, exiting...")
        sys.exit(result.returncode)


def run_app():
    app_env = os.getenv("APP_ENV", "local")

    command = [
        "uvicorn",
        "app.main:app",
        "--host",
        "0.0.0.0",
        "--port",
        "8000",
    ]

    if app_env == "local":
        print("Starting application in DEVELOPMENT mode (hot reload enabled)")
        command.append("--reload")
        command.extend(["--reload-dir", "app"])
    else:
        print(f"Starting application in {app_env.upper()} mode")

    subprocess.run(command)


if __name__ == "__main__":
    run_migration()
    run_app()