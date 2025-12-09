from sqlalchemy.orm import Session
from app.models.image import Image

class ImageRepository:

    def __init__(self, db: Session):
        self.db = db

    def find_by_image_id(self, id: int) -> Image | None:
        return self.db.query(Image).filter(Image.image_id == id).first()
