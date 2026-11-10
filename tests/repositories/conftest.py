from datetime import datetime
import pytest
from sqlalchemy.orm import Session
from app.models.post import Post, PostStatus
from app.models.tag import Tag
from app.models.user import User


@pytest.fixture
def make_post(db: Session, test_user: User):
    """記事を登録して返すファクトリ"""

    def _make_post(
        slug: str,
        title: str | None = "title",
        status: PostStatus = PostStatus.DRAFT,
        published_at: datetime | None = None,
        thumbnail_url: str | None = None,
        created_at: datetime | None = None,
    ) -> Post:
        post = Post(
            user_id=test_user.user_id,
            title=title,
            slug=slug,
            content_md="md",
            content_html="<p>md</p>",
            status=status,
            published_at=published_at,
            thumbnail_url=thumbnail_url,
        )
        if created_at is not None:
            post.created_at = created_at
        db.add(post)
        db.flush()
        return post

    return _make_post


@pytest.fixture
def make_tag(db: Session):
    """タグを登録して返すファクトリ"""

    def _make_tag(name: str, slug: str) -> Tag:
        tag = Tag(name=name, slug=slug)
        db.add(tag)
        db.flush()
        return tag

    return _make_tag
