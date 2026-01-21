from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Image(Base):
    __tablename__ = "images"

    image_id = Column(BigInteger, primary_key=True, index=True)
    post_id = Column(BigInteger, ForeignKey("posts.post_id"), nullable=True, index=True)
    url = Column(String(500), nullable=False)
    alt_text = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # リレーションシップ
    post = relationship("Post", back_populates="images")
