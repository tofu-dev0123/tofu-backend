from sqlalchemy.orm import Session
from app.repositories.product_repository import ProductRepository
from app.schemas.product import Product, ProductListResponse
from app.schemas.tag import Tag


class PublicProductService:

    def __init__(self, db: Session):
        self.db = db
        self.product_repo = ProductRepository(db)

    """
    公開中のプロダクト一覧を取得する（sort 順）
    """

    def get_products(self) -> ProductListResponse:
        products = self.product_repo.find_published()

        product_list = []
        for product in products:
            tags = [
                Tag(tag_id=tag.tag_id, name=tag.name, slug=tag.slug)
                for tag in product.tags
            ]
            product_list.append(
                Product(
                    product_id=product.product_id,
                    title=product.title,
                    description=product.description,
                    link_url=product.link_url,
                    github_url=product.github_url,
                    published=product.published,
                    sort_order=product.sort_order,
                    tags=tags,
                )
            )

        return ProductListResponse(products=product_list)
