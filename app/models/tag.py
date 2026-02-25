from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import BigInteger, String, DateTime, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.post import Post


class Tag(Base):
    __tablename__ = "tags"

    tag_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)

    # リレーションシップ
    posts: Mapped[list[Post]] = relationship("Post", secondary="post_tags", back_populates="tags")
