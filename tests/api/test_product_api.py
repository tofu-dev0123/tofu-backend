from unittest.mock import patch
from app.common.errorcode import ErrorCode
from app.common.message import Message, ErrorMessage
from app.schemas.product import Product, ProductListResponse
from app.schemas.tag import Tag
from app.core.exceptions.handlers import ApplicationError


def _product_schema(product_id=1):
    return Product(
        product_id=product_id,
        title="プロダクト",
        description="説明",
        link_url="https://example.com",
        published=True,
        sort_order=0,
        tags=[Tag(tag_id=1, name="Python", slug="python")],
    )


# 正常系: プロダクト一覧取得
@patch("app.services.product_service.ProductService.get_products")
def test_get_products_success(mock_get, client, valid_token):
    mock_get.return_value = ProductListResponse(products=[_product_schema()])

    response = client.get(
        "/admin/products", headers={"Authorization": f"Bearer {valid_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["products"]) == 1
    assert data["products"][0]["tags"][0]["name"] == "Python"


# 異常系: トークンなし
def test_get_products_no_token(client):
    response = client.get("/admin/products")
    assert response.status_code == 401


# 正常系: プロダクト作成
@patch("app.services.product_service.ProductService.create_product")
def test_create_product_success(mock_create, client, valid_token):
    mock_create.return_value = 100

    req = {
        "title": "新規",
        "description": "d",
        "link_url": "https://example.com",
        "published": True,
        "sort_order": 1,
        "tags": ["python"],
    }
    response = client.post(
        "/admin/products",
        headers={"Authorization": f"Bearer {valid_token}"},
        json=req,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == Message.PRODUCT_CREATE_SUCCESS
    assert data["product_id"] == 100


# バリデーションエラー: title 欠落
def test_create_product_validation_title_missing(client, valid_token):
    response = client.post(
        "/admin/products",
        headers={"Authorization": f"Bearer {valid_token}"},
        json={},
    )

    assert response.status_code == 400
    data = response.json()
    messages = [item["message"] for item in data["details"]]
    assert data["error"] == ErrorCode.VALIDATION_ERROR
    assert ErrorMessage.PRODUCT_TITLE_REQUIRED in messages


# 正常系: プロダクト詳細取得
@patch("app.services.product_service.ProductService.get_product")
def test_get_product_success(mock_get, client, valid_token):
    mock_get.return_value = _product_schema(product_id=5)

    response = client.get(
        "/admin/products/5", headers={"Authorization": f"Bearer {valid_token}"}
    )

    assert response.status_code == 200
    assert response.json()["product_id"] == 5


# 異常系: プロダクト詳細が存在しない
@patch("app.services.product_service.ProductService.get_product")
def test_get_product_not_found(mock_get, client, valid_token):
    mock_get.side_effect = ApplicationError(
        message=ErrorMessage.PRODUCT_NOT_EXIST, code=ErrorCode.NOT_EXIST
    )

    response = client.get(
        "/admin/products/999", headers={"Authorization": f"Bearer {valid_token}"}
    )

    assert response.status_code == 400
    data = response.json()
    assert data["error"] == ErrorCode.NOT_EXIST
    assert data["message"] == ErrorMessage.PRODUCT_NOT_EXIST


# 正常系: プロダクト更新
@patch("app.services.product_service.ProductService.update_product")
def test_update_product_success(mock_update, client, valid_token):
    mock_update.return_value = None

    req = {"title": "更新", "published": False, "sort_order": 0, "tags": []}
    response = client.put(
        "/admin/products/7",
        headers={"Authorization": f"Bearer {valid_token}"},
        json=req,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == Message.PRODUCT_UPDATE_SUCCESS
    assert data["product_id"] == 7


# 正常系: プロダクト削除
@patch("app.services.product_service.ProductService.delete_product")
def test_delete_product_success(mock_delete, client, valid_token):
    mock_delete.return_value = None

    response = client.delete(
        "/admin/products/4", headers={"Authorization": f"Bearer {valid_token}"}
    )

    assert response.status_code == 200
    assert response.json()["message"] == Message.PRODUCT_DELETE_SUCCESS
