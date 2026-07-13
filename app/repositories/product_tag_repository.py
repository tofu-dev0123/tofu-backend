from sqlalchemy import delete
from sqlalchemy.orm import Session
from app.models.product_tag import ProductTag


class ProductTagRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, product_tag: ProductTag):
        self.db.add(product_tag)

    def delete_product_tags(self, product_id: int) -> None:
        stmt = delete(ProductTag).where(ProductTag.product_id == product_id)
        self.db.execute(stmt)
