from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.post import Post, PostStatus


class PostRepository:

    def __init__(self, db: Session):
        self.db = db

    def find_posts_by_user(
        self,
        user_id: int,
        offset: int,
        limit: int,
        keyword: str | None = None,
        status: PostStatus | None = None,
    ):
        statement = select(Post).where(Post.user_id == user_id)

        # keyword がある場合だけ LIKE 条件を追加
        if keyword:
            statement = statement.where(Post.title.like(f"%{keyword}%"))
            
        if status:
            statement = statement.where(Post.status == status)

        statement = (
            statement.order_by(Post.created_at.desc()).offset(offset).limit(limit)
        )

        return self.db.execute(statement).scalars().all()

    def find_slugs_like(self, slug: str) -> list[str]:
        result = self.db.query(Post.slug).filter(Post.slug.like(f"{slug}%")).all()
        return [row[0] for row in result]

    def create(self, post: Post) -> int:
        self.db.add(post)
        self.db.flush()
        return post.post_id
