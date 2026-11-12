from unittest.mock import patch
from app.schemas.product import Product, ProductListResponse
from app.schemas.tag import Tag


# 正常系: 公開プロダクト一覧の取得
@patch("app.services.public.product_service.PublicProductService.get_products")
def test_get_public_products_success(mock_get, client):
    mock_get.return_value = ProductListResponse(
        products=[
            Product(
                product_id=1,
                title="プロダクト",
                description="説明",
                link_url="https://example.com",
                github_url="https://github.com/example/repo",
                published=True,
                sort_order=0,
                tags=[Tag(tag_id=1, name="Python", slug="python")],
            )
        ]
    )

    response = client.get("/products")

    assert response.status_code == 200
    data = response.json()
    assert len(data["products"]) == 1
    assert data["products"][0]["title"] == "プロダクト"
    assert data["products"][0]["tags"][0]["name"] == "Python"
    assert data["products"][0]["github_url"] == "https://github.com/example/repo"
    mock_get.assert_called_once_with()


# 正常系: 公開プロダクトが0件
@patch("app.services.public.product_service.PublicProductService.get_products")
def test_get_public_products_empty(mock_get, client):
    mock_get.return_value = ProductListResponse(products=[])

    response = client.get("/products")

    assert response.status_code == 200
    assert response.json()["products"] == []
