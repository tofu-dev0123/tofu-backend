from typing import Optional
from datetime import datetime
from sqlalchemy import BigInteger, String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base


class Image(Base):
    __tablename__ = "images"

    image_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    post_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("posts.post_id"), nullable=True, index=True)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    alt_text: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)

    # リレーションシップ
    post = relationship("Post", back_populates="images")
