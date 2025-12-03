from sqlalchemy import Column, BigInteger, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from app.db.database import Base


class PostTag(Base):
    __tablename__ = "post_tags"

    post_id = Column(BigInteger, ForeignKey("posts.post_id"), nullable=False)
    tag_id = Column(BigInteger, ForeignKey("tags.tag_id"), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("post_id", "tag_id"),
    )

    # リレーションシップ
    post = relationship("Post", backref="post_tag_associations")
    tag = relationship("Tag", backref="post_tag_associations")

