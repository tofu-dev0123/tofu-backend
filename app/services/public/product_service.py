from sqlalchemy.orm import Session
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductListResponse
from app.services.mappers import to_product


class PublicProductService:

    def __init__(
        self,
        db: Session,
        product_repo: ProductRepository | None = None,
    ) -> None:
        self.db = db
        self.product_repo = product_repo or ProductRepository(db)

    """
    公開中のプロダクト一覧を取得する（sort 順）
    """

    def get_products(self) -> ProductListResponse:
        products = self.product_repo.find_published()

        return ProductListResponse(products=[to_product(p) for p in products])
