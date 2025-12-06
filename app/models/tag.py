from sqlalchemy import Column, BigInteger, String, DateTime, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Tag(Base):
    __tablename__ = "tags"

    tag_id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # リレーションシップ
    posts = relationship(
        "Post",
        secondary="post_tags",
        back_populates="tags"
    )

