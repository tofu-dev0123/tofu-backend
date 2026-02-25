from sqlalchemy import BigInteger, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base_class import Base


class PostTag(Base):
    __tablename__ = "post_tags"

    post_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("posts.post_id"), nullable=False)
    tag_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("tags.tag_id"), nullable=False)

    __table_args__ = (PrimaryKeyConstraint("post_id", "tag_id"),)
