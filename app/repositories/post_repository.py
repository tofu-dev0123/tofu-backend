from sqlalchemy import select, func, case, update, exists, delete
from sqlalchemy.orm import Session, selectinload
from app.models.post import Post, PostStatus
from datetime import datetime


class PostRepository:

    def __init__(self, db: Session):
        self.db = db

    def exist_check_by_post_id(self, post_id) -> bool:
        stmt = select(exists().where(Post.post_id == post_id))
        return self.db.execute(stmt).scalar()

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

    def get_post_counts(self):
        stmt = select(
            func.count(Post.post_id).label("total_count"),
            func.coalesce(
                func.sum(case((Post.status == PostStatus.PUBLISHED, 1), else_=0)),
                0,
            ).label("published_count"),
            func.coalesce(
                func.sum(case((Post.status == PostStatus.DRAFT, 1), else_=0)),
                0,
            ).label("draft_count"),
        )

        result = self.db.execute(stmt).one()

        return result

    def find_slugs_like(self, slug: str) -> list[str]:
        result = self.db.query(Post.slug).filter(Post.slug.like(f"{slug}%")).all()
        return [row[0] for row in result]

    def create(self, post: Post) -> int:
        self.db.add(post)
        self.db.flush()
        return post.post_id

    def find_by_post_id(self, id: int) -> Post:
        return self.db.query(Post).filter(Post.post_id == id).first()

    def find_thumbnail_url_by_post_id(self, id: int) -> str | None:
        stmt = select(Post.thumbnail_url).where(Post.post_id == id)
        return self.db.execute(stmt).scalar_one_or_none()

    def update_post(
        self,
        post_id: int,
        title: str,
        content_md: str,
        content_html: str,
        status: PostStatus,
        published_at: datetime | None,
        thumbnail_url: str | None,
    ):
        stmt = (
            update(Post)
            .where(Post.post_id == post_id)
            .values(
                title=title,
                content_md=content_md,
                content_html=content_html,
                status=status,
                published_at=published_at,
                thumbnail_url=thumbnail_url,
                updated_at=datetime.now(),
            )
        )
        self.db.execute(stmt)

    def update_status_and_published_at(
        self,
        post_id: int,
        status: PostStatus,
        published_at: datetime | None,
    ):
        stmt = (
            update(Post)
            .where(Post.post_id == post_id)
            .values(
                status=status,
                published_at=published_at,
                updated_at=datetime.now(),  # updated_at を管理してるなら
            )
        )
        self.db.execute(stmt)

    def delete(self, post_id):
        stmt = delete(Post).where(Post.post_id == post_id)
        self.db.execute(stmt)

    def find_published_posts(self, offset: int, limit: int, keyword: str | None = None):
        statement = (
            select(Post)
            .options(selectinload(Post.tags))
            .where(Post.status == PostStatus.PUBLISHED)
        )

        if keyword:
            statement = statement.where(Post.title.like(f"%{keyword}%"))

        statement = (
            statement.order_by(Post.published_at.desc()).offset(offset).limit(limit)
        )

        return self.db.execute(statement).scalars().all()
