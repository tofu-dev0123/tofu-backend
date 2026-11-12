from fastapi import APIRouter, Depends, Path
from app.api.deps import get_product_service
from app.core.security import get_current_user
from app.common.message import Message
from app.schemas.product import (
    Product,
    ProductListResponse,
    ProductPostRequest,
    ProductPutRequest,
    ProductResponse,
    ProductDeleteResponse,
)
from app.services.product_service import ProductService
from app.models.user import User
from app.common.constant import Constant


router = APIRouter(prefix="/products", tags=["Product プロダクト関連"])


@router.get("", response_model=ProductListResponse)
async def get_products(
    service: ProductService = Depends(get_product_service),
    current_user: User = Depends(get_current_user),
) -> ProductListResponse:
    return service.get_products()


@router.post("", response_model=ProductResponse)
async def create_product(
    request: ProductPostRequest,
    service: ProductService = Depends(get_product_service),
    current_user: User = Depends(get_current_user),
) -> ProductResponse:
    product_id = service.create_product(request)

    return ProductResponse(
        message=Message.PRODUCT_CREATE_SUCCESS, product_id=product_id
    )


@router.get("/{product_id}", response_model=Product)
async def get_product(
    product_id: int = Path(..., ge=Constant.MIN_PRODUCT_ID, description="プロダクトID"),
    service: ProductService = Depends(get_product_service),
    current_user: User = Depends(get_current_user),
) -> Product:
    return service.get_product(product_id)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    request: ProductPutRequest,
    product_id: int = Path(..., ge=Constant.MIN_PRODUCT_ID, description="プロダクトID"),
    service: ProductService = Depends(get_product_service),
    current_user: User = Depends(get_current_user),
) -> ProductResponse:
    service.update_product(product_id, request)

    return ProductResponse(
        message=Message.PRODUCT_UPDATE_SUCCESS, product_id=product_id
    )


@router.delete("/{product_id}", response_model=ProductDeleteResponse)
async def delete_product(
    product_id: int = Path(..., ge=Constant.MIN_PRODUCT_ID, description="プロダクトID"),
    service: ProductService = Depends(get_product_service),
    current_user: User = Depends(get_current_user),
) -> ProductDeleteResponse:
    service.delete_product(product_id)

    return ProductDeleteResponse(message=Message.PRODUCT_DELETE_SUCCESS)
