from sqlalchemy.orm import Session
from app.models.image import Image


def find_by_image_id(db: Session, id: int) -> Image | None:
    return db.query(Image).filter(Image.image_id == id).first()
