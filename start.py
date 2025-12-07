#!/usr/bin/env python3
"""
アプリケーション起動スクリプト
マイグレーションを実行してからアプリケーションを起動します
"""
import subprocess
import sys

if __name__ == "__main__":
    # マイグレーションを実行
    print("Running database migrations...")
    result = subprocess.run([sys.executable, "migrate_db.py"], check=False)

    if result.returncode != 0:
        print("Migration failed, exiting...")
        sys.exit(result.returncode)

    # アプリケーションを起動
    print("Starting application...")
    subprocess.run(["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"])
