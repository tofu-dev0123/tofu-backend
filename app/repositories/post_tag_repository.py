from sqlalchemy.orm import Session
from app.models.post_tag import PostTag


class PostTagRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, post_tag: PostTag):
        self.db.add(post_tag)
