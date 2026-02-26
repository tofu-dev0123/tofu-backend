from sqlalchemy import delete, select
from sqlalchemy.orm import Session
from app.models.image import Image


class ImageRepository:

    def __init__(self, db: Session):
        self.db = db

    def find_by_image_id(self, id: int) -> Image | None:
        return self.db.query(Image).filter(Image.image_id == id).first()

    def find_by_url(self, url: str) -> Image | None:
        return self.db.query(Image).filter(Image.url == url).first()

    def find_url_by_post_id(self, id: int) -> list[str]:
        stmt = select(Image.url).where(Image.post_id == id)
        return list(self.db.execute(stmt).scalars().all())

    def update_post_id(self, image_id: int, post_id: int):
        image: Image | None = self.db.query(Image).filter(Image.image_id == image_id).first()
        if image:
            image.post_id = post_id
            self.db.commit()

    def create(self, image: Image) -> int:
        self.db.add(image)
        self.db.flush()
        return image.image_id

    def delete(self, image_id: int):
        stmt = delete(Image).where(Image.image_id == image_id)
        self.db.execute(stmt)

    def delete_from_post_id(self, post_id: int):
        stmt = delete(Image).where(Image.post_id == post_id)
        self.db.execute(stmt)
