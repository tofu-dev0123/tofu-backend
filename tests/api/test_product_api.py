from unittest.mock import patch
import pytest
from pydantic import ValidationError
from app.common.errorcode import ErrorCode
from app.common.message import Message, ErrorMessage
from app.common.constant import Constant
from app.core.validation import VALIDATION_MESSAGES
from app.schemas.product import Product, ProductListResponse, ProductPostRequest
from app.schemas.tag import Tag
from app.core.exceptions.application_exceptions import ApplicationError


def _product_schema(product_id=1):
    return Product(
        product_id=product_id,
        title="プロダクト",
        description="説明",
        link_url="https://example.com",
        github_url="https://github.com/example/repo",
        published=True,
        sort_order=0,
        tags=[Tag(tag_id=1, name="Python", slug="python")],
    )


# 正常系: プロダクト一覧取得
@patch("app.services.product_service.ProductService.get_products")
def test_get_products_success(mock_get, client, auth_headers):
    mock_get.return_value = ProductListResponse(products=[_product_schema()])

    response = client.get(
        "/admin/products", headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["products"]) == 1
    assert data["products"][0]["tags"][0]["name"] == "Python"
    assert (
        data["products"][0]["github_url"] == "https://github.com/example/repo"
    )


# 異常系: トークンなし
def test_get_products_no_token(client):
    response = client.get("/admin/products")
    assert response.status_code == 401


# 正常系: プロダクト作成
@patch("app.services.product_service.ProductService.create_product")
def test_create_product_success(mock_create, client, auth_headers):
    mock_create.return_value = 100

    req = {
        "title": "新規",
        "description": "d",
        "link_url": "https://example.com",
        "github_url": "https://github.com/example/repo",
        "published": True,
        "sort_order": 1,
        "tags": ["python"],
    }
    response = client.post(
        "/admin/products",
        headers=auth_headers,
        json=req,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == Message.PRODUCT_CREATE_SUCCESS
    assert data["product_id"] == 100


# バリデーションエラー: title 欠落
def test_create_product_validation_title_missing(client, auth_headers):
    response = client.post(
        "/admin/products",
        headers=auth_headers,
        json={},
    )

    assert response.status_code == 400
    data = response.json()
    messages = [item["message"] for item in data["details"]]
    assert data["error"] == ErrorCode.VALIDATION_ERROR
    assert ErrorMessage.PRODUCT_TITLE_REQUIRED in messages


# バリデーションエラー: タイトルの文字数上限超過（記事用ではなくプロダクト用のメッセージ）
def test_create_product_validation_title_too_long(client, auth_headers):
    response = client.post(
        "/admin/products",
        headers=auth_headers,
        json={"title": "a" * (Constant.MAX_PRODUCT_TITLE_LENGTH + 1)},
    )

    assert response.status_code == 400
    data = response.json()
    messages = [item["message"] for item in data["details"]]
    assert data["error"] == ErrorCode.VALIDATION_ERROR
    assert ErrorMessage.PRODUCT_TITLE_MAX_LENGTH in messages


# タイトル超過のエラー type がプロダクト固有である
# （現状は記事と上限・文言が同じため、type で記事用メッセージと区別されることを確認する）
def test_product_title_too_long_error_type():
    with pytest.raises(ValidationError) as exc_info:
        ProductPostRequest(title="a" * (Constant.MAX_PRODUCT_TITLE_LENGTH + 1))

    errors = exc_info.value.errors()
    assert errors[0]["loc"] == ("title",)
    assert errors[0]["type"] == "product_title_too_long"
    assert VALIDATION_MESSAGES[("title", "product_title_too_long")] == (
        ErrorMessage.PRODUCT_TITLE_MAX_LENGTH
    )


# 正常系: タイトルが文字数上限ちょうど
@patch("app.services.product_service.ProductService.create_product")
def test_create_product_title_max_length_boundary(mock_create, client, auth_headers):
    mock_create.return_value = 100

    response = client.post(
        "/admin/products",
        headers=auth_headers,
        json={"title": "a" * Constant.MAX_PRODUCT_TITLE_LENGTH},
    )

    assert response.status_code == 200


# バリデーションエラー: タグの個数上限超過
def test_create_product_validation_tags_too_many(client, auth_headers):
    response = client.post(
        "/admin/products",
        headers=auth_headers,
        json={"title": "新規", "tags": ["a"] * (Constant.MAX_TAGS + 1)},
    )

    assert response.status_code == 400
    data = response.json()
    messages = [item["message"] for item in data["details"]]
    assert data["error"] == ErrorCode.VALIDATION_ERROR
    assert ErrorMessage.TAGS_ARRAY_MAX_LENGTH in messages


# バリデーションエラー: タグの文字数上限超過
def test_create_product_validation_tag_too_long(client, auth_headers):
    response = client.post(
        "/admin/products",
        headers=auth_headers,
        json={"title": "新規", "tags": ["a" * (Constant.MAX_TAG_LENGTH + 1)]},
    )

    assert response.status_code == 400
    data = response.json()
    messages = [item["message"] for item in data["details"]]
    assert data["error"] == ErrorCode.VALIDATION_ERROR
    assert ErrorMessage.TAGS_MAX_LENGTH in messages


# 空文字の description / link_url / github_url は None に変換される
@patch("app.services.product_service.ProductService.create_product")
def test_create_product_empty_string_to_none(mock_create, client, auth_headers):
    mock_create.return_value = 100

    response = client.post(
        "/admin/products",
        headers=auth_headers,
        json={"title": "新規", "description": "", "link_url": "", "github_url": ""},
    )

    assert response.status_code == 200
    request = mock_create.call_args.args[0]
    assert request.description is None
    assert request.link_url is None
    assert request.github_url is None


# 正常系: プロダクト詳細取得
@patch("app.services.product_service.ProductService.get_product")
def test_get_product_success(mock_get, client, auth_headers):
    mock_get.return_value = _product_schema(product_id=5)

    response = client.get(
        "/admin/products/5", headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json()["product_id"] == 5


# 異常系: プロダクト詳細が存在しない
@patch("app.services.product_service.ProductService.get_product")
def test_get_product_not_found(mock_get, client, auth_headers):
    mock_get.side_effect = ApplicationError(
        message=ErrorMessage.PRODUCT_NOT_EXIST, code=ErrorCode.NOT_EXIST
    )

    response = client.get(
        "/admin/products/999", headers=auth_headers
    )

    assert response.status_code == 400
    data = response.json()
    assert data["error"] == ErrorCode.NOT_EXIST
    assert data["message"] == ErrorMessage.PRODUCT_NOT_EXIST


# 正常系: プロダクト更新
@patch("app.services.product_service.ProductService.update_product")
def test_update_product_success(mock_update, client, auth_headers):
    mock_update.return_value = None

    req = {"title": "更新", "published": False, "sort_order": 0, "tags": []}
    response = client.put(
        "/admin/products/7",
        headers=auth_headers,
        json=req,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == Message.PRODUCT_UPDATE_SUCCESS
    assert data["product_id"] == 7


# 正常系: プロダクト削除
@patch("app.services.product_service.ProductService.delete_product")
def test_delete_product_success(mock_delete, client, auth_headers):
    mock_delete.return_value = None

    response = client.delete(
        "/admin/products/4", headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json()["message"] == Message.PRODUCT_DELETE_SUCCESS
