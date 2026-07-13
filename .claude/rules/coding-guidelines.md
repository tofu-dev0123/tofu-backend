# コーディング規約

本ドキュメントでは、バックエンド API のコーディング規約について説明する。

## 設計原則

### レイヤー構造の遵守

- controller / service / repository の責務を明確に分離する
- controller（API 層）にビジネスロジックを書かない
- 既存のレイヤ構造を崩さない

### 責務の分離

- 副作用のある処理は service 層に集約する
- repository 層はデータアクセスのみに専念する
- 複雑なクエリは `repositories/queries/` に分離する

## 命名規則

### ファイル・モジュール

- スネークケース（snake_case）を使用する
- 機能ごとにファイルを分割する

```
post_service.py
post_repository.py
auth_exceptions.py
```

### クラス

- PascalCase を使用する

```python
class PostService:
    ...

class PostRepository:
    ...

class PostStatus(Enum):
    ...
```

### 関数・メソッド

- スネークケースを使用する
- 動詞で始める

```python
def create_post():
    ...

def get_post_detail():
    ...

def find_by_post_id():
    ...
```

### 変数

- スネークケースを使用する

```python
post_id = 1
user_id = 1
content_md = "..."
```

### 定数

- SCREAMING_SNAKE_CASE を使用する

```python
MAX_TITLE_LENGTH = 255
ALLOWED_EXTENSIONS = {"jpeg", "jpg", "png", "heic"}
```

## 型定義

### 明示的な型定義

すべての関数・メソッドで引数と戻り値の型を明示する。

```python
def create_post(self, request: PostCreateRequest, user_id: int) -> PostResponse:
    ...

def find_by_id(self, post_id: int) -> Post | None:
    ...
```

### Pydantic スキーマ

リクエスト・レスポンスには Pydantic スキーマを使用する。

```python
class PostCreateRequest(BaseModel):
    title: str = Field(..., max_length=Constant.MAX_TITLE_LENGTH)
    content_md: str = Field(...)
    tag_names: list[str] = Field(default_factory=list)
```

## バリデーション

### Pydantic によるバリデーション

- Field による制約を使用する
- 複雑なバリデーションには field_validator を使用する

```python
class PostCreateRequest(BaseModel):
    title: str = Field(..., max_length=Constant.MAX_TITLE_LENGTH)
    content_md: str = Field(...)

    @field_validator("content_md")
    def validate_content_md_size(cls, v):
        if len(v.encode("utf-8")) > Constant.MAX_CONTENT_MARKDOWN_SIZE:
            raise PydanticCustomError("size_over", "")
        return v
```

### 定数の使用

バリデーションに使用する値は `common/constant.py` で定義する。

```python
class Constant:
    MAX_TITLE_LENGTH = 255
    MAX_CONTENT_MARKDOWN_SIZE = 1 * 1024 * 1024  # 1MB
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS = {"jpeg", "jpg", "png", "heic"}
    MAX_TAGS = 20
    MAX_TAG_LENGTH = 30
```

## エラーハンドリング

### カスタム例外

機能ごとにカスタム例外を定義する。

```python
# 認証例外
class AuthenticationError(Exception):
    ...

class LoginFailError(Exception):
    ...

# 画像例外
class ImageNotExistError(Exception):
    ...

class ImageUploadValidationError(Exception):
    ...
```

### エラーコード

エラーコードは `common/errorcode.py` で定義する。

```python
class ErrorCode:
    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    LOGIN_FAIL = "LOGIN_FAIL"
    NOT_EXIST = "NOT_EXIST"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
```

### エラーレスポンス

統一されたエラーレスポンス形式を使用する。

```json
{
  "message": "エラーメッセージ",
  "error": "ERROR_CODE",
  "details": [{ "value": "field", "message": "詳細" }]
}
```

## メッセージ管理

### 成功メッセージ

`common/message.py` の Message クラスで定義する。

```python
class Message:
    LOGIN_SUCCESS = "ログインに成功しました"
    POST_CREATE_SUCCESS = "記事を作成しました"
```

### エラーメッセージ

`common/message.py` の ErrorMessage クラスで定義する。

```python
class ErrorMessage:
    AUTHENTICATION_ERROR = "認証に失敗しました"
    LOGIN_FAIL = "ユーザー名またはパスワードが間違っています"
```

## 依存性注入

### FastAPI Depends の使用

サービス・リポジトリの注入には Depends を使用する。

```python
def get_post_service(db: Session = Depends(get_db)) -> PostService:
    return PostService(db)

@router.post("/")
async def create_post(
    request: PostCreateRequest,
    service: PostService = Depends(get_post_service),
    current_user: User = Depends(get_current_user),
):
    return service.create_post(request, current_user.user_id)
```

## トランザクション管理

### Service 層での管理

トランザクションは Service 層で管理する。

```python
def create_post(self, request: PostCreateRequest, user_id: int) -> PostResponse:
    try:
        # DB操作
        post = self.post_repository.create(...)
        self.tag_repository.create_bulk(...)
        self.db.commit()
        return PostResponse(...)
    except:
        self.db.rollback()
        raise
```

## ロギング

### logger の使用

```python
import logging

logger = logging.getLogger(__name__)

def some_function():
    try:
        ...
    except Exception as e:
        logger.exception("エラーメッセージ")
        raise
```

## テスト

### テスト構成

```
tests/
├── api/                  # APIエンドポイントテスト
├── services/             # サービスロジックテスト
├── mock_data/            # モックデータ
└── conftest.py           # テスト設定
```

### テスト方針

- ビジネスロジックにはユニットテストを書く
- 外部サービス（DB / S3）はモックする

### テストフレームワーク

- pytest を使用する

## 禁止事項

- 指示されていない範囲の変更は禁止
- 無関係なリファクタリングは禁止
- 既存 API の仕様変更は事前確認が必要
- データモデルの変更は慎重に行う
