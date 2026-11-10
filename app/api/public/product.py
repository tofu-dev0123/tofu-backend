from fastapi import APIRouter, Depends
from app.api.deps import get_public_product_service
from app.schemas.product import ProductListResponse
from app.services.public.product_service import PublicProductService


router = APIRouter(prefix="/products", tags=["Product 公開プロダクト関連"])


@router.get("", response_model=ProductListResponse)
def get_products(
    service: PublicProductService = Depends(get_public_product_service),
):
    return service.get_products()
