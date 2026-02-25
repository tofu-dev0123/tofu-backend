from sqlalchemy.orm import Session
from app.models.tag import Tag

from sqlalchemy.orm import Session
from app.models.tag import Tag


class TagRepository:

    def __init__(self, db: Session):
        self.db = db

    def find_id_by_name(self, name: str) -> int | None:
        result = self.db.query(Tag.tag_id).filter(Tag.name == name).first()
        return result[0] if result else None

    def find_slugs_starting_with(self, slug_base: str) -> list[str]:
        result = self.db.query(Tag.slug).filter(Tag.slug.like(f"{slug_base}%")).all()
        return [row[0] for row in result]

    def create(self, name: str, slug: str) -> int:
        tag = Tag(name=name, slug=slug)
        self.db.add(tag)
        self.db.flush()
        return tag.tag_id
