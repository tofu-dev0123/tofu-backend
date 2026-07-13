import pytest
from io import BytesIO
from fastapi import UploadFile
from starlette.datastructures import Headers
from unittest.mock import MagicMock
from app.services.auth_service import AuthService
from app.services.post_service import PostService
from app.services.image_service import ImageService
from app.services.account_service import AccountService
from app.services.tag_service import TagService
from app.services.profile_service import ProfileService
from app.services.timeline_service import TimelineService
from app.services.product_service import ProductService


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def tag_service(mock_db):
    return TagService(mock_db)


@pytest.fixture
def profile_service(mock_db):
    return ProfileService(mock_db)


@pytest.fixture
def timeline_service(mock_db):
    return TimelineService(mock_db)


@pytest.fixture
def product_service(mock_db):
    return ProductService(mock_db)


@pytest.fixture
def auth_service(mock_db):
    return AuthService(mock_db)


@pytest.fixture
def post_service(mock_db):
    return PostService(mock_db)


@pytest.fixture
def image_service(mock_db):
    return ImageService(mock_db)


@pytest.fixture
def account_service(mock_db):
    return AccountService(mock_db)


@pytest.fixture
def upload_file():
    return UploadFile(
        filename="test.png",
        file=BytesIO(b"dummy image"),
        headers=Headers({"content-type": "image/png"}),
    )
