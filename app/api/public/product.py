from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.product import ProductListResponse
from app.services.public.product_service import PublicProductService


router = APIRouter(prefix="/products", tags=["Product 公開プロダクト関連"])


def get_product_service(db: Session = Depends(get_db)) -> PublicProductService:
    return PublicProductService(db)


@router.get("", response_model=ProductListResponse)
async def get_products(
    service: PublicProductService = Depends(get_product_service),
):
    return service.get_products()
