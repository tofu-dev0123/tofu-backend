import pytest
from unittest.mock import MagicMock, Mock
from app.services.public.product_service import PublicProductService
from app.schemas.tag import Tag


@pytest.fixture
def public_product_service(mock_db):
    return PublicProductService(mock_db, product_repo=MagicMock())


def _mock_tag(tag_id: int, name: str, slug: str) -> Mock:
    tag = Mock()
    tag.tag_id = tag_id
    tag.name = name
    tag.slug = slug
    return tag


# 公開中のプロダクトをタグ付きで返す
def test_get_products_success(public_product_service):
    product = Mock()
    product.product_id = 1
    product.title = "title"
    product.description = None
    product.link_url = None
    product.github_url = "https://github.com/example/repo"
    product.published = True
    product.sort_order = 0
    product.tags = [_mock_tag(10, "Python", "python")]
    public_product_service.product_repo.find_published.return_value = [product]

    result = public_product_service.get_products()

    assert len(result.products) == 1
    assert result.products[0].product_id == 1
    assert result.products[0].github_url == "https://github.com/example/repo"
    assert result.products[0].tags == [Tag(tag_id=10, name="Python", slug="python")]
    public_product_service.product_repo.find_published.assert_called_once_with()


# 公開中のプロダクトがない場合は空リスト
def test_get_products_empty(public_product_service):
    public_product_service.product_repo.find_published.return_value = []

    result = public_product_service.get_products()

    assert result.products == []
