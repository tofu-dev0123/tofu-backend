from sqlalchemy import Column, BigInteger, ForeignKey, PrimaryKeyConstraint
from app.db.base_class import Base


class ProductTag(Base):
    __tablename__ = "product_tags"

    product_id = Column(BigInteger, ForeignKey("products.product_id"), nullable=False)
    tag_id = Column(BigInteger, ForeignKey("tags.tag_id"), nullable=False)

    __table_args__ = (PrimaryKeyConstraint("product_id", "tag_id"),)
