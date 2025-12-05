from sqlalchemy import Column, BigInteger, String, DateTime, Enum, ForeignKey, func
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy.orm import relationship
import enum
from app.db.base_class import Base


class PostStatus(enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"


class Post(Base):
    __tablename__ = "posts"

    post_id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    content_md = Column(MEDIUMTEXT, nullable=False)
    content_html = Column(MEDIUMTEXT, nullable=False)
    thumbnail_url = Column(String(500), nullable=True)
    status = Column(Enum(PostStatus), nullable=False, default=PostStatus.DRAFT)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # リレーションシップ
    user = relationship("User", back_populates="posts")
    tags = relationship(
        "Tag",
        secondary="post_tags",
        back_populates="posts"
    )
    images = relationship("Image", back_populates="post", cascade="all, delete-orphan")

