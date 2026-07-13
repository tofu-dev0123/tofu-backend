import pytest
from unittest.mock import MagicMock, Mock
from app.schemas.product import ProductPostRequest, ProductPutRequest
from app.core.exceptions.handlers import ApplicationError
from app.common.errorcode import ErrorCode
from app.common.message import ErrorMessage


def _mock_product(product_id=1, published=True):
    mock_tag = Mock()
    mock_tag.tag_id = 1
    mock_tag.name = "Python"
    mock_tag.slug = "python"

    product = Mock()
    product.product_id = product_id
    product.title = "プロダクト"
    product.description = "説明"
    product.link_url = "https://example.com"
    product.published = published
    product.sort_order = 0
    product.tags = [mock_tag]
    return product


# get_products: 正常系
def test_get_products_success(product_service):
    product_service.product_repo = MagicMock()
    product_service.product_repo.find_all.return_value = [_mock_product()]

    result = product_service.get_products()

    assert len(result.products) == 1
    assert result.products[0].product_id == 1
    assert result.products[0].tags[0].name == "Python"


# get_product: 正常系
def test_get_product_success(product_service):
    product_service.product_repo = MagicMock()
    product_service.product_repo.find_by_id.return_value = _mock_product(product_id=5)

    result = product_service.get_product(5)

    assert result.product_id == 5
    assert result.title == "プロダクト"


# get_product: 存在しない場合
def test_get_product_not_exist(product_service):
    product_service.product_repo = MagicMock()
    product_service.product_repo.find_by_id.return_value = None

    with pytest.raises(ApplicationError) as exc_info:
        product_service.get_product(999)

    assert exc_info.value.code == ErrorCode.NOT_EXIST
    assert exc_info.value.message == ErrorMessage.PRODUCT_NOT_EXIST


# create_product: 正常系（タグ登録あり）
def test_create_product_success(product_service):
    product_service.product_repo = MagicMock()
    product_service.product_repo.create.return_value = 100
    product_service.product_tag_repo = MagicMock()
    product_service.tag_service = MagicMock()
    product_service.tag_service.get_or_create_tag_ids.return_value = [10, 20]
    product_service.db = MagicMock()

    req = ProductPostRequest(
        title="新規",
        description="desc",
        link_url="https://example.com",
        published=True,
        sort_order=1,
        tags=["python", "fastapi"],
    )

    result = product_service.create_product(req)

    assert result == 100
    product_service.tag_service.get_or_create_tag_ids.assert_called_once_with(
        ["python", "fastapi"]
    )
    assert product_service.product_tag_repo.create.call_count == 2
    product_service.db.commit.assert_called_once()


# update_product: 正常系
def test_update_product_success(product_service):
    product_service.product_repo = MagicMock()
    product_service.product_repo.exist_check.return_value = True
    product_service.product_tag_repo = MagicMock()
    product_service.tag_service = MagicMock()
    product_service.tag_service.get_or_create_tag_ids.return_value = [10]
    product_service.db = MagicMock()

    req = ProductPutRequest(
        title="更新",
        description="d",
        link_url=None,
        published=False,
        sort_order=2,
        tags=["python"],
    )

    result = product_service.update_product(7, req)

    assert result is None
    product_service.product_repo.update.assert_called_once_with(
        7, "更新", "d", None, False, 2
    )
    product_service.product_tag_repo.delete_product_tags.assert_called_once_with(7)
    product_service.db.commit.assert_called_once()


# update_product: 存在しない場合はロールバック
def test_update_product_not_exist(product_service):
    product_service.product_repo = MagicMock()
    product_service.product_repo.exist_check.return_value = False
    product_service.db = MagicMock()

    req = ProductPutRequest(
        title="x", description=None, link_url=None, published=False, sort_order=0, tags=[]
    )

    with pytest.raises(ApplicationError) as exc_info:
        product_service.update_product(7, req)

    assert exc_info.value.code == ErrorCode.NOT_EXIST
    product_service.db.rollback.assert_called_once()
    product_service.product_repo.update.assert_not_called()


# delete_product: 正常系
def test_delete_product_success(product_service):
    product_service.product_repo = MagicMock()
    product_service.product_repo.exist_check.return_value = True
    product_service.product_tag_repo = MagicMock()
    product_service.db = MagicMock()

    result = product_service.delete_product(4)

    assert result is None
    product_service.product_tag_repo.delete_product_tags.assert_called_once_with(4)
    product_service.product_repo.delete.assert_called_once_with(4)
    product_service.db.commit.assert_called_once()


# delete_product: 存在しない場合はロールバック
def test_delete_product_not_exist(product_service):
    product_service.product_repo = MagicMock()
    product_service.product_repo.exist_check.return_value = False
    product_service.db = MagicMock()

    with pytest.raises(ApplicationError) as exc_info:
        product_service.delete_product(4)

    assert exc_info.value.code == ErrorCode.NOT_EXIST
    product_service.db.rollback.assert_called_once()
    product_service.product_repo.delete.assert_not_called()
