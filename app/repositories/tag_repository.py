from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.tag import Tag


class TagRepository:

    def __init__(self, db: Session) -> None:
        self.db = db

    def find_id_by_name(self, name: str) -> int | None:
        stmt = select(Tag.tag_id).where(Tag.name == name)
        return self.db.execute(stmt).scalars().first()

    def find_slugs_starting_with(self, slug_base: str) -> list[str]:
        stmt = select(Tag.slug).where(Tag.slug.like(f"{slug_base}%"))
        return list(self.db.execute(stmt).scalars().all())

    def create(self, name: str, slug: str) -> int:
        tag = Tag(name=name, slug=slug)
        self.db.add(tag)
        self.db.flush()
        return tag.tag_id
