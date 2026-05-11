# プロジェクト概要

本リポジトリはブログプラットフォームのバックエンド API です。
保守性・テスト容易性・拡張性を重視した設計を維持します。

## ドキュメント

詳細は `docs/` を参照してください。

- [アーキテクチャ](docs/architecture.md) — 技術スタック、レイヤー構造、データベース設計、API 設計
- [コーディング規約](docs/coding-guidelines.md) — 命名規則、型定義、バリデーション、エラーハンドリング
- [テストガイドライン](docs/testing-guidelines.md) — テストの書き方とディレクトリ構成
- [アカウント管理 API](docs/api-account.md) — アカウント情報変更、パスワード変更、メールアドレス変更

## スタック概要

- **FastAPI** + **SQLAlchemy 2.0**（`Mapped[T] = mapped_column()` 記法）+ **Pydantic v2**
- **PostgreSQL 16**（`psycopg` 3.x）
- **Alembic** マイグレーション
- **pytest** テスト（**Docker 上で実行**）
- **pyright** 型チェック（`pyrightconfig.json` あり）

## 開発フロー

### ブランチ運用

- `develop` を起点にブランチを切る
- Issue 対応: `feature/issue#<番号>`
- その他: `feature/<topic>` / `fix/<topic>` / `chore/<topic>`
- リリース: `release/v<バージョン>` → `main` へマージ後タグ付与

### コミット規約

- メッセージは **日本語** で簡潔に書く
- 1 コミット 1 論理変更
- `Co-Authored-By: Claude` 行は **付けない**

### PR

- base ブランチは `develop`
- `🤖 Generated with Claude Code` などの機械生成フッターは **付けない**

## 実行・テスト

- **アプリ起動**: `docker compose up`（api: http://localhost:8000、db: PostgreSQL 16、localstack: S3 互換）
- **テスト**: Python パッケージはホストに無いため **必ず Docker 上で実行**
  - 例: `docker compose run --rm api pytest`
- **型チェック**: `pyright` をホストで実行（`pyrightconfig.json` の `reportMissingImports: false` に依存）

## Claude への指示

- 既存 API の仕様を変更する場合は **必ず事前確認** すること
- データモデルの変更は慎重に行うこと
- **指示されていない範囲の変更は禁止**
- 詳細なコーディング規約は [docs/coding-guidelines.md](docs/coding-guidelines.md) を参照

## 進行中の作業

- **Lambda + Neon 移行**（Issue #44）: Railway → AWS Lambda + Neon Free への移行
  - フェーズ毎の sub-issue に分割済み。最新状況は GitHub Issues を参照

## ファイル・ディレクトリ規約

- 環境変数: `.env.local`（リポジトリ管理）/ `.env`・`.env.production`（**コミット禁止**）
- Claude 個人設定: `.claude/settings.local.json`（gitignore 済）
- 一時的な調査スクリプト等は作らない。必要ならコミットしないこと
