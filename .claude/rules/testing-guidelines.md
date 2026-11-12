# テストガイドライン

本ドキュメントでは、バックエンド API のテストの書き方について説明する。

## 概要

テストフレームワークには pytest を使用する。テストは大きく分けて以下の 2 種類がある。

- **API テスト**: エンドポイントの動作を検証する
- **サービステスト**: ビジネスロジックを検証する

## ディレクトリ構成

```
tests/
├── conftest.py              # 共通フィクスチャ定義
├── api/                     # APIエンドポイントテスト
│   ├── test_login_api.py
│   ├── test_logout_api.py
│   ├── test_me_api.py
│   └── ...
├── services/                # サービスロジックテスト
│   ├── conftest.py          # サービステスト用フィクスチャ
│   ├── test_auth_service.py
│   └── ...
└── mock_data/               # モックデータ
    └── post_detail.py
```

## 共通フィクスチャ

### tests/conftest.py

テスト全体で使用するフィクスチャを定義する。

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token
from app.models.user import User
from app.db.database import get_db
from app.models.user import Base

TEST_DATABASE_URL = "postgresql+psycopg://blog_user:password@db:5432/test_db"

# データベースがなければ作成
if not database_exists(TEST_DATABASE_URL):
    create_database(TEST_DATABASE_URL)

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def client():
    """FastAPI テストクライアント"""
    return TestClient(app)


# FastAPI の get_db をテスト用 DB に置き換える
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def db():
    """テスト用 DB セッション（テストごとにリセット）"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db):
    """テスト用ユーザー"""
    user = User(
        user_id=1,
        username="test@example.com",
        password="password",
        account_name="testuser",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def valid_token(test_user):
    """認証済みトークン"""
    token = create_access_token(
        user_id=test_user.user_id,
        username=test_user.username
    )
    return token
```

### tests/services/conftest.py

サービステスト用のフィクスチャを定義する。

```python
import pytest
from unittest.mock import MagicMock
from app.services.auth_service import AuthService
from app.services.post_service import PostService
from app.services.image_service import ImageService


@pytest.fixture
def mock_db():
    """モック DB セッション"""
    return MagicMock()


@pytest.fixture
def auth_service(mock_db):
    """AuthService インスタンス"""
    return AuthService(mock_db)


@pytest.fixture
def post_service(mock_db):
    """PostService インスタンス"""
    return PostService(mock_db)


@pytest.fixture
def image_service(mock_db):
    """ImageService インスタンス"""
    return ImageService(mock_db)
```

## API テストの書き方

### 基本構成

```python
import pytest
from unittest.mock import patch
from app.common.errorcode import ErrorCode
from app.common.message import Message, ErrorMessage
from app.common.constant import Constant


# 正常系
def test_機能名_success(client, valid_token):
    response = client.メソッド(
        "/エンドポイント",
        headers={"Authorization": f"Bearer {valid_token}"},
        json={...}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == Message.期待するメッセージ


# 異常系
def test_機能名_error_case(client):
    response = client.メソッド("/エンドポイント", json={...})

    assert response.status_code == 400
    data = response.json()
    assert data["error"] == ErrorCode.期待するエラーコード
```

### 正常系テスト例

```python
def test_login_success(client):
    with patch(
        "app.services.auth_service.AuthService.login",
        return_value="fake_token"
    ):
        response = client.post(
            "/admin/auth/login",
            json={"username": "admin@example.com", "password": "correctpass"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == Message.LOGIN_SUCCESS
    assert data["token"] == "fake_token"
```

### 認証が必要なエンドポイントのテスト

```python
def test_logout_success(client, valid_token):
    response = client.post(
        "/admin/auth/logout",
        headers={"Authorization": f"Bearer {valid_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == Message.LOGOUT_SUCCESS
```

### バリデーションエラーのテスト

```python
# 必須項目のバリデーション
def test_validation_error_missing(client):
    response = client.post("/admin/auth/login", json={})

    assert response.status_code == 400
    data = response.json()
    messages = [item["message"] for item in data["details"]]

    assert data["error"] == ErrorCode.VALIDATION_ERROR
    assert ErrorMessage.USERNAME_REQUIRED in messages
    assert ErrorMessage.PASSWORD_REQUIRED in messages


# 最大文字数のバリデーション
def test_validation_error_max_length(client):
    big_username = "a" * (Constant.MAX_USERNAME_LENGTH + 1)
    big_password = "a" * (Constant.MAX_PASSWORD_LENGTH + 1)
    username = f"{big_username}@example.com"
    request = {"username": username, "password": big_password}
    response = client.post("/admin/auth/login", json=request)

    assert response.status_code == 400
    data = response.json()
    messages = [item["message"] for item in data["details"]]

    assert data["error"] == ErrorCode.VALIDATION_ERROR
    assert ErrorMessage.USERNAME_MAX_LENGTH in messages
    assert ErrorMessage.PASSWORD_MAX_LENGTH in messages


# 最小文字数のバリデーション
def test_validation_error_min_length(client):
    small_password = "a" * (Constant.MIN_PASSWORD_LENGTH - 1)
    username = "admin@example.com"
    request = {"username": username, "password": small_password}
    response = client.post("/admin/auth/login", json=request)

    assert response.status_code == 400
    data = response.json()
    messages = [item["message"] for item in data["details"]]

    assert data["error"] == ErrorCode.VALIDATION_ERROR
    assert ErrorMessage.PASSWORD_MIN_LENGTH in messages
```

### 認証エラーのテスト

```python
def test_not_token_authentication_error(client):
    response = client.post("/admin/auth/logout")

    assert response.status_code == 401
    data = response.json()
    assert data["message"] == ErrorMessage.TOKEN_REQUIRED
```

### 例外発生時のテスト

```python
from app.core.exceptions.auth_exceptions import LoginFailError

def test_login_fail_no_exist_username(client):
    username = "error@example.com"
    password = "password"
    request = {"username": username, "password": password}

    with patch(
        "app.services.auth_service.AuthService.login",
        side_effect=LoginFailError
    ):
        response = client.post("/admin/auth/login", json=request)

    assert response.status_code == 400
    data = response.json()
    assert data["message"] == ErrorMessage.LOGIN_FAIL
    assert data["error"] == ErrorCode.LOGIN_FAIL
```

## サービステストの書き方

### 基本構成

```python
import pytest
from unittest.mock import Mock, MagicMock, patch
from app.core.exceptions.auth_exceptions import LoginFailError


def test_サービスメソッド_success(service_fixture):
    # モックの設定
    mock_entity = Mock()
    mock_entity.id = 1
    mock_entity.name = "test"

    service_fixture.repository = MagicMock()
    service_fixture.repository.find_by_id.return_value = mock_entity

    # 外部依存のモック
    with patch("app.services.xxx.external_function", return_value=True):
        result = service_fixture.some_method(...)

    # アサーション
    assert result == expected
    assert service_fixture.repository.find_by_id.call_count == 1


def test_サービスメソッド_raises_exception(service_fixture):
    service_fixture.repository = MagicMock()
    service_fixture.repository.find_by_id.return_value = None

    with pytest.raises(SomeException):
        service_fixture.some_method(...)
```

### 正常系テスト例

```python
def test_login_success(auth_service):
    mock_user = Mock()
    mock_user.user_id = 1
    mock_user.username = "testuser"
    mock_user.password = "hashed_password"

    auth_service.user_repo = MagicMock()
    auth_service.user_repo.find_by_username.return_value = mock_user

    with patch("app.services.auth_service.verify_password", return_value=True), \
         patch("app.services.auth_service.create_access_token", return_value="fake_token"):

        result = auth_service.login("testuser", "correct_password")

        assert result == "fake_token"
        assert auth_service.user_repo.find_by_username.call_count == 1
```

### 例外発生テスト例

```python
def test_login_user_not_found(auth_service):
    auth_service.user_repo = MagicMock()
    auth_service.user_repo.find_by_username.return_value = None

    with pytest.raises(LoginFailError):
        auth_service.login("testuser", "correct_password")

    assert auth_service.user_repo.find_by_username.call_count == 1


def test_login_wrong_password(auth_service):
    mock_user = Mock()
    mock_user.user_id = 1
    mock_user.username = "testuser"
    mock_user.password = "hashed_password"

    auth_service.user_repo = MagicMock()
    auth_service.user_repo.find_by_username.return_value = mock_user

    with patch("app.services.auth_service.verify_password", return_value=False):
        with pytest.raises(LoginFailError):
            auth_service.login("testuser", "correct_password")

    assert auth_service.user_repo.find_by_username.call_count == 1
```

## 命名規則

### テストファイル名

```
test_<機能名>_<レイヤー>.py
```

例:
- `test_login_api.py`
- `test_auth_service.py`
- `test_post_get_api.py`

### テスト関数名

```
test_<機能>_<状態>
```

例:
- `test_login_success` - 正常系
- `test_login_fail_no_exist_username` - ユーザーが存在しない場合
- `test_validation_error_missing` - 必須項目バリデーションエラー
- `test_validation_error_max_length` - 最大文字数バリデーションエラー
- `test_not_token_authentication_error` - トークンなし認証エラー

## テスト実行

### 全テスト実行

```bash
pytest
```

### 特定のテストファイル実行

```bash
pytest tests/api/test_login_api.py
```

### 特定のテスト関数実行

```bash
pytest tests/api/test_login_api.py::test_login_success
```

### 詳細出力

```bash
pytest -v
```

## モック使用の指針

### patch を使用する場面

- 外部サービス（S3、外部 API）の呼び出し
- サービス層のメソッド（API テスト時）
- セキュリティ関連の関数（パスワード検証、トークン生成）

### MagicMock を使用する場面

- リポジトリの戻り値設定
- DB セッションのモック

### Mock を使用する場面

- エンティティ（User, Post など）のモック

## アサーションのパターン

### ステータスコードの検証

```python
assert response.status_code == 200
assert response.status_code == 400
assert response.status_code == 401
```

### レスポンスボディの検証

```python
data = response.json()
assert data["message"] == Message.LOGIN_SUCCESS
assert data["error"] == ErrorCode.VALIDATION_ERROR
```

### バリデーションエラーの検証

```python
data = response.json()
messages = [item["message"] for item in data["details"]]
assert ErrorMessage.USERNAME_REQUIRED in messages
```

### メソッド呼び出し回数の検証

```python
assert service.repository.find_by_id.call_count == 1
```

### 例外発生の検証

```python
with pytest.raises(LoginFailError):
    auth_service.login("testuser", "wrong_password")
```
