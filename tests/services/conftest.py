import pytest
from unittest.mock import MagicMock
from app.services.auth_service import AuthService
from app.services.post_service import PostService

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def auth_service(mock_db):
    return AuthService(mock_db)

@pytest.fixture
def post_service(mock_db):
    return PostService(mock_db)