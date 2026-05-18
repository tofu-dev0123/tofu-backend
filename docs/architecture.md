# アーキテクチャ

本ドキュメントでは、バックエンド API のアーキテクチャについて説明する。

## 技術スタック

| カテゴリ           | 技術                    |
| ------------------ | ----------------------- |
| フレームワーク     | FastAPI                 |
| ORM                | SQLAlchemy 2.0          |
| バリデーション     | Pydantic v2             |
| データベース       | PostgreSQL 16           |
| DB ドライバ        | psycopg 3.x             |
| マイグレーション   | Alembic                 |
| 認証               | JWT (python-jose)       |
| ストレージ         | AWS S3 / LocalStack     |
| コンテナ           | Docker / Docker Compose |

## ディレクトリ構造

```
backend/
├── app/
│   ├── main.py                 # FastAPIアプリケーション設定
│   ├── api/                    # APIエンドポイント
│   │   ├── admin/              # 管理者用API
│   │   │   ├── auth.py         # 認証エンドポイント
│   │   │   ├── post.py         # 記事管理エンドポイント
│   │   │   ├── image.py        # 画像管理エンドポイント
│   │   │   └── router.py       # 管理ルーター集約
│   │   ├── public/             # 公開API
│   │   │   ├── post.py         # 公開記事エンドポイント
│   │   │   └── router.py       # 公開ルーター集約
│   │   └── router.py           # 全ルーター集約
│   ├── core/                   # コア機能
│   │   ├── config.py           # 環境変数設定
│   │   ├── security.py         # JWT認証・パスワード管理
│   │   ├── validation.py       # バリデーションメッセージ
│   │   └── exceptions/         # カスタム例外
│   ├── db/                     # データベース設定
│   │   ├── base_class.py       # SQLAlchemyベースモデル
│   │   └── database.py         # DB接続設定
│   ├── models/                 # SQLAlchemy ORMモデル
│   ├── schemas/                # Pydanticスキーマ
│   ├── services/               # ビジネスロジック
│   ├── repositories/           # データアクセス層
│   │   └── queries/            # 複雑なクエリ
│   ├── infra/                  # インフラ層
│   │   └── storage/            # ストレージ操作
│   ├── common/                 # 共通定義
│   │   ├── constant.py         # 定数
│   │   ├── errorcode.py        # エラーコード
│   │   └── message.py          # メッセージ定義
│   └── utils/                  # ユーティリティ
├── tests/                      # テストコード
├── alembic/                    # マイグレーション
├── cdk/                        # AWS CDK プロジェクト (IaC)
└── docker-compose.yml          # ローカル開発環境構成
```

## レイヤー構造

本プロジェクトはクリーンアーキテクチャに基づいたレイヤー構造を採用している。

```
┌─────────────────────────────────┐
│       API Layer (Router)        │  ← リクエスト/レスポンス処理
├─────────────────────────────────┤
│        Service Layer            │  ← ビジネスロジック
├─────────────────────────────────┤
│       Repository Layer          │  ← データアクセス
├─────────────────────────────────┤
│     Infrastructure Layer        │  ← 外部サービス連携
├─────────────────────────────────┤
│         Model Layer             │  ← ORMモデル定義
└─────────────────────────────────┘
```

### API Layer

- ルーティングとリクエスト/レスポンスの処理を担当
- FastAPI の Depends による依存性注入
- Pydantic スキーマによる入力バリデーション
- ビジネスロジックを含まない

### Service Layer

- ビジネスロジックの実装
- 複数リポジトリの組み合わせ
- トランザクション管理（commit/rollback）
- 外部サービス（S3 等）との連携

### Repository Layer

- データベース操作のみに専念
- SQLAlchemy Select による型安全なクエリ
- 複雑なクエリは `queries/` に分離

### Infrastructure Layer

- 外部サービスとの連携
- S3 ストレージ操作

### Model Layer

- SQLAlchemy ORM モデル定義
- テーブル間のリレーションシップ

## データベース設計

### テーブル構成

```
users
├── user_id (PK)
├── username (UNIQUE)
├── password (bcrypt hash)
├── account_name
├── created_at
└── updated_at

posts
├── post_id (PK)
├── user_id (FK → users)
├── title
├── slug (UNIQUE)
├── content_md (TEXT)
├── content_html (TEXT)
├── thumbnail_url
├── status (ENUM: DRAFT/PUBLISHED)
├── published_at
├── created_at
└── updated_at

tags
├── tag_id (PK)
├── name (UNIQUE)
├── slug (UNIQUE)
└── created_at

post_tags (中間テーブル)
├── post_id (FK)
└── tag_id (FK)

images
├── image_id (PK)
├── post_id (FK, NULLABLE)
├── url
├── alt_text
└── created_at
```

## API 設計

### 管理者 API (/admin)

| メソッド | パス                     | 説明             |
| -------- | ------------------------ | ---------------- |
| POST     | /admin/auth/login        | ログイン         |
| POST     | /admin/auth/logout       | ログアウト       |
| GET      | /admin/posts             | 記事一覧取得     |
| POST     | /admin/posts             | 記事作成         |
| GET      | /admin/posts/{post_id}   | 記事詳細取得     |
| PUT      | /admin/posts/{post_id}   | 記事更新         |
| DELETE   | /admin/posts/{post_id}   | 記事削除         |
| PATCH    | /admin/posts/{post_id}   | ステータス変更   |
| GET      | /admin/posts/summary     | 記事統計取得     |
| POST     | /admin/images/upload     | 画像アップロード |
| DELETE   | /admin/images/{image_id} | 画像削除         |

### 公開 API

| メソッド | パス           | 説明             |
| -------- | -------------- | ---------------- |
| GET      | /posts         | 公開記事一覧取得 |
| GET      | /posts/{slug}  | 公開記事詳細取得 |

## 認証・セキュリティ

### JWT 認証

- トークン有効期限: 3 時間
- アルゴリズム: HS256
- ペイロード: user_id, username, exp

### 認証ヘッダー

```
Authorization: Bearer <JWT_TOKEN>
```

### パスワード管理

- ハッシュ化: bcrypt

## 環境構成

### ローカル環境

- Docker Compose で構築
- PostgreSQL 16
- LocalStack（S3 互換ストレージ）

### 本番・staging 環境

```
[Browser]
    ↓ https://api.tofubase.com (prod) / https://dev-api.tofubase.com (dev)
[CloudFront] ─── ACM 証明書
    ↓
[Lambda Function URL]
    ↓
[Lambda Function (Python 3.12 / ARM64)]
    ↓
[Neon Postgres] / [AWS S3] / [AWS SSM Parameter Store]
```

- 計算基盤: AWS Lambda + Function URL + CloudFront (CDK 管理)
- DB: Neon Postgres (main branch = prod / dev branch = staging)
- 画像: AWS S3 + CloudFront (CDK 管理外、AWS Console 管理)
- secrets: SSM Parameter Store `/blog-platform-backend/<env>/{DATABASE_URL,SECRET_KEY}` を Lambda が起動時に runtime fetch
- リージョン: `us-east-1` (Neon のリージョン制約に追従)

### IaC

- AWS CDK (Python) — `backend/cdk/`
- `cdk deploy -c env=dev` / `cdk deploy -c env=prod` で環境別に deploy
- `.env.dev` / `.env.prod` (gitignore 済) から非 secret 値を読む

### 環境変数

| 変数名                                          | 説明                                                                   |
| ----------------------------------------------- | ---------------------------------------------------------------------- |
| APP_ENV                                         | 環境（local/staging/production）。local 以外は SSM 経由 secret 取得    |
| DATABASE_URL                                    | Postgres 接続文字列（local 以外、または `_SSM` 経由）                   |
| DATABASE_URL_SSM / SECRET_KEY_SSM               | Lambda 用: SSM パラメータ名を指定すると起動時に値を取得して上書き      |
| DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME | local 専用（Docker Postgres 接続）                                     |
| AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY        | local 用ダミー（Lambda 上では実行ロールから取得）                       |
| S3_BUCKET_NAME, S3_ENDPOINT_URL                 | S3 設定（S3_ENDPOINT_URL は LocalStack 用、本番は未設定）              |
| CLOUDFRONT_DOMAIN                               | 画像配信用 CloudFront ドメイン                                          |
| SECRET_KEY                                      | JWT 署名キー（local 以外は SSM から取得）                               |
| ALGORITHM                                       | JWT 署名アルゴリズム（HS256）                                           |
| CORS_ALLOW_ORIGINS                              | CORS 許可オリジン（JSON 配列）                                          |
| CUSTOM_DOMAIN                                   | CDK 専用: カスタムドメイン名（指定で CloudFront + ACM が作成される）   |

## 依存性注入パターン

FastAPI の Depends を使用した依存性注入を採用している。

```python
def get_post_service(db: Session = Depends(get_db)) -> PostService:
    return PostService(db)

@router.get("/")
async def get_posts(
    service: PostService = Depends(get_post_service),
    current_user: User = Depends(get_current_user),
):
    ...
```

## トランザクション管理

Service 層でトランザクションを管理する。

```python
try:
    # 複数のDB操作
    self.db.commit()
except:
    self.db.rollback()
    raise
```
