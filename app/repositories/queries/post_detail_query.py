from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.post import Post
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
                func.group_concat(
                    func.distinct(
                        func.concat(Image.image_id, "|", Image.url, "|", Image.alt_text)
                    )
                ).label("images"),
                func.group_concat(
                    func.distinct(func.concat(Tag.tag_id, "|", Tag.name, "|", Tag.slug))
                ).label("tags"),
            )
            .join(Image, Image.post_id == Post.post_id, isouter=True)
            .join(PostTag, PostTag.post_id == Post.post_id, isouter=True)
            .join(Tag, Tag.tag_id == PostTag.tag_id, isouter=True)
            .where(Post.post_id == post_id)
            .group_by(Post.post_id)
        )

        return self.db.execute(stmt).one_or_none()
