# tests/conftest.py

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token
from app.models.user import User
from app.models.post import Post
from app.models.tag import Tag
from app.models.post_tag import PostTag
from app.models.image import Image


# ユーザーのモデルが Base を含んでる
from app.models.user import Base

TEST_DATABASE_URL = "mysql+pymysql://root:password@db:3306/test_db"

# データベースがなければ作成
if not database_exists(TEST_DATABASE_URL):
    create_database(TEST_DATABASE_URL)
    
engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db):
    user = User(
        user_id=1,
        username="test@example.com",
        password="password",
        account_name="testuser"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def valid_token(test_user):
    token = create_access_token(
        user_id=test_user.user_id,
        username=test_user.username
    )
    return token