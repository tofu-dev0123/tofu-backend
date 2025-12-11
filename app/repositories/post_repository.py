from sqlalchemy.orm import Session
from app.models.post import Post


class PostRepository:

    def __init__(self, db: Session):
        self.db = db

    def find_slugs_like(self, slug: str) -> list[str]:
        result = self.db.query(Post.slug).filter(Post.slug.like(f"{slug}%")).all()
        return [row[0] for row in result]

    def create(self, post: Post) -> int:
        self.db.add(post)
        self.db.flush()
        return post.post_id
