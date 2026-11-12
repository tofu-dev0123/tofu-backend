import pytest
from io import BytesIO
from fastapi import UploadFile
from starlette.datastructures import Headers
from datetime import datetime
from unittest.mock import MagicMock
from app.services.auth_service import AuthService
from app.services.post_service import PostService
from app.services.image_service import ImageService
from app.services.account_service import AccountService
from app.services.tag_service import TagService
from app.services.profile_service import ProfileService
from app.services.timeline_service import TimelineService
from app.services.product_service import ProductService


FIXED_NOW = datetime(2025, 1, 1, 12, 0, 0)


@pytest.fixture
def fixed_now():
    """PostService 等に注入する固定の現在時刻"""
    return FIXED_NOW


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def tag_service(mock_db):
    return TagService(mock_db, tag_repo=MagicMock())


@pytest.fixture
def profile_service(mock_db):
    return ProfileService(mock_db, profile_repo=MagicMock())


@pytest.fixture
def timeline_service(mock_db):
    return TimelineService(mock_db, timeline_repo=MagicMock())


@pytest.fixture
def product_service(mock_db):
    return ProductService(
        mock_db,
        product_repo=MagicMock(),
        product_tag_repo=MagicMock(),
        tag_service=MagicMock(),
    )


@pytest.fixture
def auth_service(mock_db):
    return AuthService(mock_db, user_repo=MagicMock())


@pytest.fixture
def post_service(mock_db, fixed_now):
    return PostService(
        mock_db,
        s3=MagicMock(),
        post_repo=MagicMock(),
        tag_service=MagicMock(),
        post_tag_repo=MagicMock(),
        image_repo=MagicMock(),
        query_repo=MagicMock(),
        now=lambda: fixed_now,
    )


@pytest.fixture
def image_service(mock_db):
    return ImageService(mock_db, image_repo=MagicMock(), s3=MagicMock())


@pytest.fixture
def account_service(mock_db):
    return AccountService(mock_db, user_repo=MagicMock())


@pytest.fixture
def upload_file():
    return UploadFile(
        filename="test.png",
        file=BytesIO(b"dummy image"),
        headers=Headers({"content-type": "image/png"}),
    )
