# アカウント管理 API

本ドキュメントでは、アカウント管理 API の仕様について説明する。

## 概要

アカウント管理 API は、ログインユーザー自身のアカウント情報を変更するための機能を提供する。

## エンドポイント一覧

| メソッド | パス                       | 説明               | 認証 |
| -------- | -------------------------- | ------------------ | ---- |
| PATCH    | /admin/account             | アカウント情報変更 | 必須 |
| PATCH    | /admin/account/password    | パスワード変更     | 必須 |
| PATCH    | /admin/account/email       | メールアドレス変更 | 必須 |

## アカウント情報変更

### エンドポイント

```
PATCH /admin/account
```

### 説明

ログインユーザーのアカウント名を変更する。

### リクエストヘッダー

| ヘッダー      | 値                   | 必須 |
| ------------- | -------------------- | ---- |
| Authorization | Bearer {JWT_TOKEN}   | Yes  |
| Content-Type  | application/json     | Yes  |

### リクエストボディ

| フィールド   | 型     | 必須 | 制約                | 説明           |
| ------------ | ------ | ---- | ------------------- | -------------- |
| account_name | string | Yes  | 1〜30 文字          | アカウント名   |

### リクエスト例

```json
{
  "account_name": "新しいアカウント名"
}
```

### レスポンス

#### 成功時 (200 OK)

```json
{
  "message": "アカウント情報を更新しました",
  "user_id": 1,
  "account_name": "新しいアカウント名"
}
```

#### エラー時

| ステータス | エラーコード         | 説明                       |
| ---------- | -------------------- | -------------------------- |
| 401        | AUTHENTICATION_ERROR | 認証に失敗した             |
| 400        | VALIDATION_ERROR     | バリデーションエラー       |

## パスワード変更

### エンドポイント

```
PATCH /admin/account/password
```

### 説明

ログインユーザーのパスワードを変更する。セキュリティのため、現在のパスワードの確認が必要。

### リクエストヘッダー

| ヘッダー      | 値                   | 必須 |
| ------------- | -------------------- | ---- |
| Authorization | Bearer {JWT_TOKEN}   | Yes  |
| Content-Type  | application/json     | Yes  |

### リクエストボディ

| フィールド       | 型     | 必須 | 制約            | 説明               |
| ---------------- | ------ | ---- | --------------- | ------------------ |
| current_password | string | Yes  | 8〜50 文字      | 現在のパスワード   |
| new_password     | string | Yes  | 8〜50 文字      | 新しいパスワード   |

### リクエスト例

```json
{
  "current_password": "current_password123",
  "new_password": "new_password456"
}
```

### レスポンス

#### 成功時 (200 OK)

```json
{
  "message": "パスワードを変更しました"
}
```

#### エラー時

| ステータス | エラーコード         | 説明                           |
| ---------- | -------------------- | ------------------------------ |
| 400        | PASSWORD_MISMATCH    | 現在のパスワードが一致しない   |
| 401        | AUTHENTICATION_ERROR | 認証に失敗した                 |
| 422        | VALIDATION_ERROR     | バリデーションエラー           |

## メールアドレス変更

### エンドポイント

```
PATCH /admin/account/email
```

### 説明

ログインユーザーのメールアドレス（ログイン ID）を変更する。セキュリティのため、現在のメールアドレスとパスワードの確認が必要。

### リクエストヘッダー

| ヘッダー      | 値                   | 必須 |
| ------------- | -------------------- | ---- |
| Authorization | Bearer {JWT_TOKEN}   | Yes  |
| Content-Type  | application/json     | Yes  |

### リクエストボディ

| フィールド      | 型     | 必須 | 制約                        | 説明                     |
| --------------- | ------ | ---- | --------------------------- | ------------------------ |
| current_email   | string | Yes  | メール形式、50 文字以下     | 現在のメールアドレス     |
| new_email       | string | Yes  | メール形式、50 文字以下     | 新しいメールアドレス     |
| password        | string | Yes  | 8〜50 文字                  | 現在のパスワード         |

### リクエスト例

```json
{
  "current_email": "old-email@example.com",
  "new_email": "new-email@example.com",
  "password": "current_password123"
}
```

### レスポンス

#### 成功時 (200 OK)

```json
{
  "message": "メールアドレスを変更しました",
  "user_id": 1,
  "username": "new-email@example.com"
}
```

#### エラー時

| ステータス | エラーコード         | 説明                                   |
| ---------- | -------------------- | -------------------------------------- |
| 400        | PASSWORD_MISMATCH    | パスワードが一致しない                 |
| 400        | EMAIL_MISMATCH       | 現在のメールアドレスが一致しない       |
| 400        | EMAIL_ALREADY_EXISTS | メールアドレスが既に使用されている     |
| 401        | AUTHENTICATION_ERROR | 認証に失敗した                         |
| 422        | VALIDATION_ERROR     | バリデーションエラー                   |

## バリデーションルール

### アカウント名

- 必須項目
- 1 文字以上 30 文字以下
- 空白のみは不可

### パスワード

- 必須項目
- 8 文字以上 50 文字以下
- 現在のパスワードと新しいパスワードが同一の場合はエラー

### メールアドレス

- 必須項目
- 有効なメールアドレス形式
- 50 文字以下
- 他のユーザーが使用しているメールアドレスは不可
- 現在のメールアドレスと同一の場合はエラー

## 実装時の注意事項

### セキュリティ

- パスワード変更時は必ず現在のパスワードを確認する
- メールアドレス変更時は必ず現在のパスワードを確認する
- 新しいパスワードは bcrypt でハッシュ化して保存する
- パスワード/メールアドレス変更後、既存のトークンは無効化しない（必要に応じて検討）
- メールアドレスの重複チェックを行う

### トランザクション

- アカウント情報の更新は Service 層でトランザクション管理を行う

### ファイル構成

実装時に作成・変更するファイル:

```
app/
├── api/admin/
│   └── account.py              # 新規: エンドポイント定義
├── schemas/
│   └── account.py              # 新規: リクエスト/レスポンススキーマ
├── services/
│   └── account_service.py      # 新規: ビジネスロジック
├── repositories/
│   └── user_repository.py      # 変更: 更新メソッド追加
├── core/exceptions/
│   └── account_exceptions.py   # 新規: カスタム例外
└── common/
    ├── errorcode.py            # 変更: エラーコード追加
    └── message.py              # 変更: メッセージ追加
```

### 追加するエラーコード

```python
# common/errorcode.py
PASSWORD_MISMATCH = "PASSWORD_MISMATCH"
EMAIL_MISMATCH = "EMAIL_MISMATCH"
EMAIL_ALREADY_EXISTS = "EMAIL_ALREADY_EXISTS"
```

### 追加するメッセージ

```python
# common/message.py
class Message:
    ACCOUNT_UPDATE_SUCCESS = "アカウント情報を更新しました"
    PASSWORD_CHANGE_SUCCESS = "パスワードを変更しました"
    EMAIL_CHANGE_SUCCESS = "メールアドレスを変更しました"

class ErrorMessage:
    PASSWORD_MISMATCH = "現在のパスワードが正しくありません"
    EMAIL_MISMATCH = "現在のメールアドレスが正しくありません"
    EMAIL_ALREADY_EXISTS = "このメールアドレスは既に使用されています"
```
