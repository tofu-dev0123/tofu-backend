from datetime import datetime
from sqlalchemy import select, update, delete, exists
from sqlalchemy.orm import Session, selectinload
from app.models.product import Product


class ProductRepository:

    def __init__(self, db: Session):
        self.db = db

    def exist_check(self, product_id: int) -> bool:
        stmt = select(exists().where(Product.product_id == product_id))
        return bool(self.db.execute(stmt).scalar())

    def find_all(self):
        stmt = (
            select(Product)
            .options(selectinload(Product.tags))
            .order_by(Product.sort_order.asc(), Product.product_id.asc())
        )
        return self.db.execute(stmt).scalars().all()

    def find_published(self):
        stmt = (
            select(Product)
            .options(selectinload(Product.tags))
            .where(Product.published.is_(True))
            .order_by(Product.sort_order.asc(), Product.product_id.asc())
        )
        return self.db.execute(stmt).scalars().all()

    def find_by_id(self, product_id: int) -> Product | None:
        stmt = (
            select(Product)
            .options(selectinload(Product.tags))
            .where(Product.product_id == product_id)
        )
        return self.db.execute(stmt).scalars().first()

    def create(self, product: Product) -> int:
        self.db.add(product)
        self.db.flush()
        return product.product_id

    def update(
        self,
        product_id: int,
        title: str,
        description: str | None,
        link_url: str | None,
        github_url: str | None,
        published: bool,
        sort_order: int,
    ) -> None:
        stmt = (
            update(Product)
            .where(Product.product_id == product_id)
            .values(
                title=title,
                description=description,
                link_url=link_url,
                github_url=github_url,
                published=published,
                sort_order=sort_order,
                updated_at=datetime.now(),
            )
        )
        self.db.execute(stmt)

    def delete(self, product_id: int) -> None:
        stmt = delete(Product).where(Product.product_id == product_id)
        self.db.execute(stmt)
