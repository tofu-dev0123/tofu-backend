#!/usr/bin/env bash
# pytest (Docker) と pyright を実行し、成功したら HEAD の sha を .claude/.last-check に記録する。
# .claude/hooks/require-check.sh が git push / gh pr create 時にこの記録と HEAD を照合する。
#
# ホストの 5432 が他プロジェクトと衝突しても動くよう、db はポートを公開せずに起動し
# (--use-aliases で "db" のエイリアスを付与)、api は --no-deps で実行する。
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

MARKER="$ROOT/.claude/.last-check"
DB_CONTAINER="blog-db-check"

cleanup() {
  docker rm -f "$DB_CONTAINER" >/dev/null 2>&1 || true
}
trap cleanup EXIT

rm -f "$MARKER"

echo "==> pyright"
pyright

echo "==> db を起動"
cleanup
docker compose run -d --use-aliases --name "$DB_CONTAINER" db >/dev/null
for _ in $(seq 1 30); do
  if docker exec "$DB_CONTAINER" pg_isready -U blog_user -d blog_db >/dev/null 2>&1; then
    break
  fi
  sleep 1
done
docker exec "$DB_CONTAINER" pg_isready -U blog_user -d blog_db >/dev/null

echo "==> pytest"
docker compose run --rm --no-deps api pytest "$@"

if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
  echo "==> チェックは成功しましたが、未コミットの変更があるため記録しません。コミット後に再実行してください。" >&2
  exit 1
fi

git rev-parse HEAD > "$MARKER"
echo "==> OK: $(cat "$MARKER") を記録しました"
