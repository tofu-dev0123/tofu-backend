#!/usr/bin/env python3
"""
Phase 2 (#47) 用: Railway MySQL → Neon Postgres データ移行スクリプト

実行例:
    docker compose run --rm api bash -c "pip install pymysql cryptography --quiet && \
        ENV_FILE=.env.staging APP_ENV=staging python migrate_from_mysql.py"

--truncate を付けると移行前に Postgres 側のテーブルを空にする (再実行用)
Phase 6 (Railway 解約) 完了後にこのファイルは削除して良い
"""
import argparse
import os
import sys

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session


# 移行対象テーブル (FK 依存順)
MIGRATION_ORDER = ["users", "tags", "posts", "post_tags", "images"]

# 各テーブルの sequence と PK 列 (setval 用)
SEQUENCES = [
    ("users_user_id_seq", "users", "user_id"),
    ("tags_tag_id_seq", "tags", "tag_id"),
    ("posts_post_id_seq", "posts", "post_id"),
    ("images_image_id_seq", "images", "image_id"),
]


def normalize_mysql_url(url: str) -> str:
    if url.startswith("mysql://"):
        return "mysql+pymysql://" + url[len("mysql://"):]
    return url


def get_columns(engine, table: str) -> list[str]:
    """MySQL の SHOW COLUMNS でカラム一覧を取得"""
    with engine.connect() as c:
        rows = c.execute(text(f"SHOW COLUMNS FROM `{table}`")).all()
    return [r[0] for r in rows]


def migrate_table(src_engine, dst_engine, table: str) -> tuple[int, int]:
    """SELECT * FROM src.table → INSERT INTO dst.table"""
    src_cols = get_columns(src_engine, table)
    src_count = 0
    dst_count = 0

    with src_engine.connect() as src:
        rows = src.execute(text(f"SELECT * FROM `{table}`")).mappings().all()
        src_count = len(rows)

    if not rows:
        return (0, 0)

    col_list = ", ".join(src_cols)
    placeholders = ", ".join(f":{c}" for c in src_cols)
    insert_sql = text(f"INSERT INTO {table} ({col_list}) VALUES ({placeholders})")

    with dst_engine.begin() as dst:
        for row in rows:
            dst.execute(insert_sql, dict(row))
        dst_count = src_count

    return (src_count, dst_count)


def setval_sequences(dst_engine):
    with dst_engine.begin() as dst:
        for seq, table, pk in SEQUENCES:
            dst.execute(
                text(
                    f"SELECT setval('{seq}', COALESCE((SELECT MAX({pk}) FROM {table}), 1), "
                    f"(SELECT MAX({pk}) FROM {table}) IS NOT NULL)"
                )
            )
            print(f"  setval({seq}) done")


def truncate_dst(dst_engine):
    # FK を考慮した順で TRUNCATE CASCADE
    with dst_engine.begin() as dst:
        for t in reversed(MIGRATION_ORDER):
            dst.execute(text(f"TRUNCATE TABLE {t} RESTART IDENTITY CASCADE"))
            print(f"  truncated {t}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--truncate",
        action="store_true",
        help="移行前に Postgres 側を TRUNCATE (再実行用、危険)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="件数だけ表示して移行は行わない",
    )
    args = parser.parse_args()

    load_dotenv(".env.staging")

    src_url = os.environ.get("LEGACY_MYSQL_URL")
    if not src_url:
        print("ERROR: LEGACY_MYSQL_URL not set in .env.staging", file=sys.stderr)
        sys.exit(1)
    src_url = normalize_mysql_url(src_url)

    # 接続先 Postgres は app.core.config.settings.database_url を使う
    # (.env.staging の DATABASE_URL から構築される)
    from app.core.config import settings

    dst_url = settings.database_url

    src = create_engine(src_url)
    dst = create_engine(dst_url)

    print("=== Source (MySQL) ===")
    with src.connect() as c:
        print("  Server:", c.execute(text("SELECT version()")).scalar())
    print("=== Destination (Postgres) ===")
    with dst.connect() as c:
        print("  Server:", c.execute(text("SELECT version()")).scalar()[:60])
    print()

    print("=== Row counts ===")
    for t in MIGRATION_ORDER:
        with src.connect() as c:
            sc = c.execute(text(f"SELECT COUNT(*) FROM `{t}`")).scalar()
        with dst.connect() as c:
            dc = c.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
        print(f"  {t}: source={sc}, destination={dc}")
    print()

    if args.dry_run:
        print("(dry-run mode, exiting)")
        return

    if args.truncate:
        print("=== TRUNCATE destination ===")
        truncate_dst(dst)
        print()

    print("=== Migrating ===")
    for t in MIGRATION_ORDER:
        src_n, dst_n = migrate_table(src, dst, t)
        ok = "OK" if src_n == dst_n else "MISMATCH"
        print(f"  {t}: {src_n} → {dst_n} [{ok}]")
    print()

    print("=== setval sequences ===")
    setval_sequences(dst)
    print()

    print("=== Final row counts ===")
    for t in MIGRATION_ORDER:
        with dst.connect() as c:
            dc = c.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
        print(f"  {t}: {dc}")
    print()
    print("Migration complete.")


if __name__ == "__main__":
    main()
