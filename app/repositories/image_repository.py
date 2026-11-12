from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session
from app.models.image import Image


class ImageRepository:

    def __init__(self, db: Session) -> None:
        self.db = db

    def find_by_image_id(self, id: int) -> Image | None:
        stmt = select(Image).where(Image.image_id == id)
        return self.db.execute(stmt).scalars().first()

    def find_by_image_ids(self, ids: list[int]) -> list[Image]:
        stmt = select(Image).where(Image.image_id.in_(ids))
        return list(self.db.execute(stmt).scalars().all())

    def find_by_url(self, url: str) -> Image | None:
        stmt = select(Image).where(Image.url == url)
        return self.db.execute(stmt).scalars().first()

    def find_url_by_post_id(self, id: int) -> list[str]:
        stmt = select(Image.url).where(Image.post_id == id)
        return list(self.db.execute(stmt).scalars().all())

    def update_post_id_by_image_ids(self, image_ids: list[int], post_id: int) -> None:
        stmt = update(Image).where(Image.image_id.in_(image_ids)).values(post_id=post_id)
        self.db.execute(stmt)

    def create(self, image: Image) -> int:
        self.db.add(image)
        self.db.flush()
        return image.image_id

    def delete(self, image_id: int) -> None:
        stmt = delete(Image).where(Image.image_id == image_id)
        self.db.execute(stmt)

    def delete_by_image_ids(self, ids: list[int]) -> None:
        stmt = delete(Image).where(Image.image_id.in_(ids))
        self.db.execute(stmt)

    def delete_from_post_id(self, post_id: int) -> None:
        stmt = delete(Image).where(Image.post_id == post_id)
        self.db.execute(stmt)
