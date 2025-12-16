from sqlalchemy.orm import Session
from app.models.image import Image


class ImageRepository:

    def __init__(self, db: Session):
        self.db = db

    def find_by_image_id(self, id: int) -> Image | None:
        return self.db.query(Image).filter(Image.image_id == id).first()

    def update_post_id(self, image_id: int, post_id: int):
        image: Image = self.db.query(Image).filter(Image.image_id == image_id).first()
        if image:
            image.post_id = post_id
            self.db.commit()
            
    def create(self, image: Image) -> int:
        self.db.add(image)
        self.db.flush()
        return image.image_id
