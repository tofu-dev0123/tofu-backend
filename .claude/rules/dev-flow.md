# 開発フロー（Issue 駆動）

本リポジトリの開発は、Issue 起票を起点に以下のスキルで進める。

```
/feature <トピック>  ─┐
/bugfix  <トピック>  ─┴→ 影響調査 → 改修案提示 ⏸確定 → Issue 起票

/implement <Issue番号>
  → Issue 確認 → 実装計画提示 ⏸承認 → 計画を Issue にコメント
  → ブランチ作成 → 実装 → テスト → レビュー(code-reviewer) →(指摘修正)→ PR 作成

  (人間がレビュー・マージ ⏸)

/cleanup <Issue番号>
  → マージ確認 → Issue クローズ確認 → ブランチ削除 → develop 同期
```

⏸ はユーザーの承認ゲート。承認なしに先へ進まない。マージは人間が行う。

## 構成

| 種別 | パス | 役割 |
| ---- | ---- | ---- |
| skill | `.claude/skills/feature/` | 機能追加の影響調査 → 起票（`enhancement`） |
| skill | `.claude/skills/bugfix/` | バグの原因・影響調査 → 起票（`bug`） |
| skill | `.claude/skills/implement/` | 計画 → 実装 → テスト → レビュー → PR |
| skill | `.claude/skills/cleanup/` | マージ後の後片付け |
| agent | `.claude/agents/code-reviewer.md` | 差分レビュー（読み取り専用） |
| script | `scripts/check.sh` | pyright + pytest(Docker)。成功時に HEAD の sha を `.claude/.last-check` に記録 |
| hook | `.claude/hooks/require-check.sh` | `feature/*` `fix/*` での `git push` / `gh pr create` を、HEAD でチェック未通過ならブロック |
| template | `.github/ISSUE_TEMPLATE/feature.md` `bugfix.md` | 起票本文の形式（スキルと共通） |
| template | `.github/pull_request_template.md` | PR 本文の形式（スキルと共通） |

グローバルの `issue` / `pr` / `commit` スキルとは名前を分けている（同名だとグローバル側が優先されるため）。
本リポジトリの Issue 対応では、上記のプロジェクトスキルを使う。

## ラベル

| ラベル | 付与タイミング |
| ------ | -------------- |
| `enhancement` | `/feature` で起票時 |
| `bug` | `/bugfix` で起票時 |
| `status:in-progress` | `/implement` で計画承認後 |
| `status:review` | `/implement` で PR 作成後（`status:in-progress` を外す） |

`/cleanup` で status ラベルを除去する。

## 記録の残し方

- 改修案（調査結果）は Issue 本文に残す
- 承認された実装計画は Issue コメントに残す（先頭に `<!-- claude:plan -->`）
- 実装上の判断理由・レビュー結果・未対応事項は PR 本文に残す

## ルール

- ブランチ: `develop` から `feature/issue#<番号>`
- コミット: 日本語、1 コミット 1 論理変更、プレフィックス（`feat:` `fix:` 等）。`git add -A` は使わない
- テスト: `scripts/check.sh` を HEAD で通してから push / PR 作成する（hook は実行前に判定するため、check.sh と push は別コマンドで実行する）
- レビュー↔修正ループは最大 3 回。残った指摘は PR の「未対応事項」に書く
- PR: base は `develop`、本文に `Closes #<番号>`
