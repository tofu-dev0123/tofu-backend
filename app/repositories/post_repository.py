from sqlalchemy.orm import Session
from app.models.post import Post

def find_slugs_like(db: Session, slug: str) -> list[str]:
    result = db.query(Post.slug).filter(Post.slug.like(f"{slug}%")).all()
    return [row[0] for row in result]
