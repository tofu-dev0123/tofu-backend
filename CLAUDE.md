# プロジェクト概要

本リポジトリはブログプラットフォームのバックエンド API です。
保守性・テスト容易性・拡張性を重視した設計を維持します。

## ドキュメント

詳細は `.claude/rules/` を参照してください。

- [アーキテクチャ](.claude/rules/architecture.md) — 技術スタック、レイヤー構造、データベース設計、API 設計、デプロイ構成
- [コーディング規約](.claude/rules/coding-guidelines.md) — 命名規則、型定義、バリデーション、エラーハンドリング
- [テストガイドライン](.claude/rules/testing-guidelines.md) — テストの書き方とディレクトリ構成
- [アカウント管理 API](.claude/rules/api-account.md) — アカウント情報変更、パスワード変更、メールアドレス変更

## スタック概要

### アプリ
- **FastAPI** + **SQLAlchemy 2.0** + **Pydantic v2**（uvicorn 直起動）
- **PostgreSQL 16**（`psycopg` 3.x）
- **Alembic** マイグレーション
- **pytest** テスト（**Docker 上で実行**）
- **pyright** 型チェック（`pyrightconfig.json` あり）

### インフラ
- 計算基盤: **AWS Lightsail** (Ubuntu 24.04 / x86_64 / 東京) 上の **docker compose**（uvicorn + Caddy）※prod のみ
- dev: **ローカル docker + Cloudflare Tunnel**（専用サーバーは持たない）
- 前段: **Cloudflare**（proxy / TLS）+ Caddy(Origin Cert, Full strict)。SSH は **Cloudflare Tunnel** 経由（22 非公開）
- DB: **Neon Postgres** (main = prod / dev = dev branch)
- 画像: **AWS S3** + **CloudFront**（据え置き）
- secrets: box の **`.env.production` 直置き**（root 600）。CI マイグレ用に `DATABASE_URL` を GitHub Environment secret にも複製
- IaC: **生 CloudFormation** — `infra/cloudformation/`（Lightsail Instance + StaticIp）
- レジストリ: **GHCR**（`ghcr.io/tofu-dev0123/tofu-backend`）
- カスタムドメイン: `api.tofubase.com` (prod)

## 開発フロー

### ブランチ運用

- `develop` を起点にブランチを切る
- Issue 対応: `feature/issue#<番号>`
- その他: `feature/<topic>` / `fix/<topic>` / `chore/<topic>`
- リリース: `release/<バージョン>` → `main` へマージ後タグ付与 (`v<バージョン>`)

### コミット規約

- メッセージは **日本語** で簡潔に書く
- 1 コミット 1 論理変更
- `Co-Authored-By: Claude` 行は **付けない**

### PR

- base ブランチは `develop`
- `🤖 Generated with Claude Code` などの機械生成フッターは **付けない**

### デプロイ

- **prod デプロイ**: `production` ブランチへ push → `deploy-prod.yml` が GHCR に amd64 イメージを build/push → Cloudflare Tunnel 経由 SSH で box の `docker compose -f docker-compose.production.yml pull && up -d`
- **DB マイグレーション**: deploy から分離。GitHub Actions の `Migrate DB`（`workflow_dispatch`、env=dev/prod 選択）で `alembic upgrade head` を Neon に適用
- **インフラ (Lightsail)**: `infra/cloudformation/cfn-tofu-lightsail.yaml` を `aws cloudformation deploy`（東京・変更頻度低のため手動）。box の初回セットアップ手順は `infra/README.md`

## 実行・テスト

- **ローカルアプリ起動**: `docker compose up`（api: http://localhost:8000、db: PostgreSQL 16、localstack: S3 互換）
- **テスト**: Python パッケージはホストに無いため **必ず Docker 上で実行**
  - 例: `docker compose run --rm api pytest`
- **型チェック**: `pyright` をホストで実行 (`nix-direnv` 経由で node が提供される)
- **インフラ検証**: `cfn-lint infra/cloudformation/*.yaml`（CI でも実行）

## Claude への指示

- 既存 API の仕様を変更する場合は **必ず事前確認** すること
- データモデルの変更は慎重に行うこと
- **指示されていない範囲の変更は禁止**
- 詳細なコーディング規約は [.claude/rules/coding-guidelines.md](.claude/rules/coding-guidelines.md) を参照

## ファイル・ディレクトリ規約

- 環境変数:
  - `.env.local` (リポジトリ管理、ローカル Docker 用ダミー値)
  - `.env.example` (リポジトリ管理、テンプレート)
  - `.env.prod` (gitignore、box の `.env.production` の元となる本番値の控え)
  - `.env` / `.env.production` (**コミット禁止**、settings.json の hook でも保護)
- 証明書・秘密鍵 (`*.pem` / `*.key`) は gitignore 済 (コミット禁止)
- Claude 個人設定: `.claude/settings.local.json`（gitignore 済）
- インフラ定義: `infra/`（`cloudformation/` に生 CFN、本番 compose / Caddyfile / README）
- 一時的な調査スクリプト等は作らない。必要ならコミットしないこと
