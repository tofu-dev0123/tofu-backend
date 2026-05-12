from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.post import Post, PostStatus
from app.models.image import Image
from app.models.post_tag import PostTag
from app.models.tag import Tag


class PostDetailQueryRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_post_id(self, post_id: int):
        stmt = (
            select(
                Post.post_id,
                Post.title,
                Post.slug,
                Post.content_md,
                Post.content_html,
                Post.thumbnail_url,
                Post.status,
                Post.published_at,
                Post.created_at,
                Post.updated_at,
                func.string_agg(
                    func.distinct(
                        func.concat_ws(
                            "|",
                            Image.image_id,
                            Image.url,
                            func.coalesce(Image.alt_text, ""),
                        )
                    ),
                    ",",
                ).label("images"),
                func.string_agg(
                    func.distinct(
                        func.concat_ws("|", Tag.tag_id, Tag.name, Tag.slug)
                    ),
                    ",",
                ).label("tags"),
            )
            .join(Image, Image.post_id == Post.post_id, isouter=True)
            .join(PostTag, PostTag.post_id == Post.post_id, isouter=True)
            .join(Tag, Tag.tag_id == PostTag.tag_id, isouter=True)
            .where(Post.post_id == post_id)
            .group_by(Post.post_id)
        )

        return self.db.execute(stmt).one_or_none()

    def find_by_slug(self, slug: str):
        stmt = (
            select(
                Post.post_id,
                Post.title,
                Post.slug,
                Post.content_html,
                Post.thumbnail_url,
                Post.published_at,
                func.string_agg(
                    func.distinct(
                        func.concat_ws("|", Tag.tag_id, Tag.name, Tag.slug)
                    ),
                    ",",
                ).label("tags"),
            )
            .join(PostTag, PostTag.post_id == Post.post_id, isouter=True)
            .join(Tag, Tag.tag_id == PostTag.tag_id, isouter=True)
            .where(Post.slug == slug)
            .where(Post.status == PostStatus.PUBLISHED)
            .group_by(Post.post_id)
        )

        return self.db.execute(stmt).one_or_none()
