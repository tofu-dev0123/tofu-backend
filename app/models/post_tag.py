from sqlalchemy import Column, BigInteger, ForeignKey, PrimaryKeyConstraint
from app.db.base_class import Base


class PostTag(Base):
    __tablename__ = "post_tags"

    post_id = Column(BigInteger, ForeignKey("posts.post_id"), nullable=False)
    tag_id = Column(BigInteger, ForeignKey("tags.tag_id"), nullable=False)

    __table_args__ = (PrimaryKeyConstraint("post_id", "tag_id"),)
