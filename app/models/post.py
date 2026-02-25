from __future__ import annotations
from datetime import datetime
from typing import Optional, TYPE_CHECKING
import enum
from sqlalchemy import BigInteger, String, DateTime, Enum, ForeignKey, func
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.tag import Tag
    from app.models.image import Image


class PostStatus(enum.Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"


class Post(Base):
    __tablename__ = "posts"

    post_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"), nullable=False, index=True)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    content_md: Mapped[str] = mapped_column(MEDIUMTEXT, nullable=False)
    content_html: Mapped[str] = mapped_column(MEDIUMTEXT, nullable=False)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    status: Mapped[PostStatus] = mapped_column(Enum(PostStatus), nullable=False, default=PostStatus.DRAFT)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # リレーションシップ
    user: Mapped[User] = relationship("User", back_populates="posts")
    tags: Mapped[list[Tag]] = relationship("Tag", secondary="post_tags", back_populates="posts")
    images: Mapped[list[Image]] = relationship("Image", back_populates="post", cascade="all, delete-orphan")
