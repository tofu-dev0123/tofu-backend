# ログガイドライン

本ドキュメントでは、バックエンド API のログ設計と各レイヤーでのログ配置方針を説明する。

## 基盤

- **標準 `logging` + 自作フォーマッタ**で構成する（追加依存なし）。
- 設定は `app/core/logging/` に集約する。
  - `config.py` — `setup_logging()`。`main.py` から初期化する。
  - `formatters.py` — `JsonFormatter` / `HumanFormatter`。
  - `context.py` — `request_id` 用 contextvar と `RequestIdFilter`。
  - `middleware.py` — `RequestLoggingMiddleware`（request_id 採番 + アクセスログ）。
- 出力先は **stdout**（docker / Cloudflare 側で収集する前提）。
- ロガーは各モジュールで `logger = logging.getLogger(__name__)` を使う。

## 環境ごとの出力形式・レベル

| 環境 | 形式 | 既定レベル |
| ---- | ---- | ---------- |
| local | 人間可読（`HumanFormatter`） | DEBUG |
| それ以外 | JSON（`JsonFormatter`） | INFO |

判定は `settings.is_local`（`APP_ENV`）による。

## JSON スキーマ

全ログ行に以下の共通フィールドを含める。

| フィールド | 説明 |
| ---------- | ---- |
| timestamp | ISO8601（UTC, ミリ秒 + `Z`） |
| level | ログレベル |
| logger | ロガー名（`%(name)s`） |
| message | メッセージ本文 |
| request_id | 相関 ID（リクエスト外は null） |

付帯フィールドは `logger.xxx(msg, extra={...})` で渡すと自動で JSON に展開される。
リクエストログでは `method` / `path` / `status_code` / `duration_ms` を付与する。
例外情報（`exc_info`）は `stack` フィールドに格納される。

## レベル使い分け

| レベル | 用途 | 例 |
| ------ | ---- | -- |
| DEBUG | 開発時の詳細（local のみ） | クエリ内容、分岐トレース |
| INFO | 正常系の重要イベント | リクエスト完了、記事作成/削除、画像アップロード成功 |
| WARNING | 異常だが処理は継続 | バリデーションエラー、認証失敗、404 |
| ERROR | 処理失敗・要調査 | S3 失敗、DB 例外、未捕捉例外 |

## request_id（相関 ID）

- `RequestLoggingMiddleware` がリクエストごとに採番する。
- リクエストヘッダ `X-Request-ID` があれば踏襲、なければ `uuid4` を生成する（Cloudflare 等との相関用）。
- 採番した ID はレスポンスヘッダ `X-Request-ID` にも返す。
- contextvar 経由で同一リクエスト内の全ログに自動注入される。

## レイヤー別ガイドライン（どこで・何を・どのレベルで）

| レイヤー | 方針 |
| -------- | ---- |
| ミドルウェア | 全リクエストの完了時に 1 行アクセスログ（INFO）。request_id 採番もここ。未捕捉例外（5xx）は ERROR（stack 付き）で 1 回だけ出す |
| API 層 | 原則ログを出さない（ミドルウェアと例外ハンドラでカバー） |
| Service 層 | 業務イベント成功時に INFO（作成/更新/削除/公開/ログイン等、エンティティ ID を付帯）。ログ配置の主戦場 |
| Repository 層 | 原則出さない（SQL は必要なら DEBUG） |
| 外部連携（S3 等） | 呼び出し失敗を ERROR（`logger.exception`）。失敗を検知したこのレイヤーで 1 回ログする |
| 例外ハンドラ | 業務 4xx（バリデーション/認証/NOT_EXIST 等）を WARNING で一元的に出す。外部要因由来のエラー（例: `S3FileUploadError`）は infra/service で既に ERROR ログ済みのため再ログしない |

> **二重ログを避ける原則**: エラーは「最初に十分な文脈を持つレイヤー」で 1 回だけログする。infra/service で ERROR を出したものは例外ハンドラで再ログしない。5xx はミドルウェアが拾う。

## 秘匿情報の扱い

- **トークン・パスワード・メールアドレス・Authorization ヘッダはログに出さない。**
- リクエストログには body / query string / ヘッダを含めない（`method` / `path` のみ）。
- `extra` に渡す値にも秘匿情報を含めないこと。

## テスト

- テストは Docker 上で実行する（`docker compose run --rm api pytest`）。
