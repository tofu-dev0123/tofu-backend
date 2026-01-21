from sqlalchemy import delete
from sqlalchemy.orm import Session
from app.models.post_tag import PostTag


class PostTagRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, post_tag: PostTag):
        self.db.add(post_tag)

    def delete_post_tags(self, post_id: int) -> None:
        stmt = delete(PostTag).where(PostTag.post_id == post_id)
        self.db.execute(stmt)
