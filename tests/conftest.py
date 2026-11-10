# tests/conftest.py

from collections.abc import Iterator
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy_utils import create_database, database_exists
from app.main import create_app
from app.core.security import create_access_token, get_current_user, hash_password
from app.db.database import get_db

# Base.metadata にテーブルを登録するため、全モデルを import しておく
from app.models.user import Base, User
from app.models.post import Post  # noqa: F401
from app.models.tag import Tag  # noqa: F401
from app.models.post_tag import PostTag  # noqa: F401
from app.models.image import Image  # noqa: F401

TEST_DATABASE_URL = "postgresql+psycopg://blog_user:password@db:5432/test_db"

# test_user の平文パスワード（DB には bcrypt ハッシュを保存する）
TEST_USER_PASSWORD = "password"


@pytest.fixture(scope="session")
def test_engine() -> Iterator[Engine]:
    """テスト用 DB の engine（生成時点では接続しない）"""
    engine = create_engine(TEST_DATABASE_URL)
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def session_factory(test_engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session")
def test_database() -> None:
    """テスト用 DB がなければ作成する（DB を使うテストでのみ接続する）"""
    if not database_exists(TEST_DATABASE_URL):
        create_database(TEST_DATABASE_URL)


@pytest.fixture
def app(session_factory: sessionmaker[Session]) -> FastAPI:
    """テストごとに生成するアプリ。dependency_overrides はこの app に閉じる"""
    application = create_app()

    def override_get_db() -> Iterator[Session]:
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    application.dependency_overrides[get_db] = override_get_db
    return application


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


@pytest.fixture
def db(
    test_database: None, test_engine: Engine, session_factory: sessionmaker[Session]
) -> Iterator[Session]:
    Base.metadata.create_all(bind=test_engine)
    session = session_factory()
    yield session
    session.close()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="session")
def test_user_password_hash() -> str:
    """bcrypt は低速なため、ハッシュはセッションで 1 回だけ計算する"""
    return hash_password(TEST_USER_PASSWORD)


@pytest.fixture
def test_user(db: Session, test_user_password_hash: str) -> User:
    user = User(
        user_id=1,
        username="test@example.com",
        password=test_user_password_hash,
        account_name="testuser",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def valid_token(test_user: User) -> str:
    token = create_access_token(user_id=test_user.user_id, username=test_user.username)
    return token


@pytest.fixture
def auth_headers(valid_token: str) -> dict[str, str]:
    """実 DB のユーザーで認証する Authorization ヘッダ"""
    return {"Authorization": f"Bearer {valid_token}"}


@pytest.fixture
def override_current_user(app: FastAPI) -> User:
    """DB を使わずに get_current_user を固定ユーザーへ差し替える"""
    user = User(
        user_id=1,
        username="test@example.com",
        password="",
        account_name="testuser",
    )
    app.dependency_overrides[get_current_user] = lambda: user
    return user
