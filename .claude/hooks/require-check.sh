#!/usr/bin/env bash
# PreToolUse(Bash) hook:
# feature/* / fix/* ブランチでの git push / gh pr create を、scripts/check.sh が
# 現在の HEAD で成功していない場合にブロックする。
set -uo pipefail

cmd=$(jq -r '.tool_input.command // empty')

case "$cmd" in
  *"git push"* | *"gh pr create"*) ;;
  *) exit 0 ;;
esac

# ブランチ削除の push は対象外
case "$cmd" in
  *"git push"*"--delete"* | *"git push"*" -d "*) exit 0 ;;
esac

cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0

branch=$(git branch --show-current 2>/dev/null)
case "$branch" in
  feature/* | fix/*) ;;
  *) exit 0 ;;
esac

marker=".claude/.last-check"
head=$(git rev-parse HEAD)

if [ ! -f "$marker" ] || [ "$(cat "$marker")" != "$head" ]; then
  echo "現在の HEAD ($head) で scripts/check.sh (pytest + pyright) が成功していません。scripts/check.sh を実行してから再試行してください。" >&2
  exit 2
fi

exit 0
