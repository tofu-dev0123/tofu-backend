import math
from sqlalchemy.orm import Session
from app.common.constant import Constant
from app.repositories.post_repository import PostRepository
from app.repositories.queries.post_detail_query import PostDetailQueryRepository
from app.schemas.post import (
    PostsPublishAtResponse,
    PostPublishAt,
    PostPublishAtResponse,
    PostSlugsResponse,
)
from app.services.guards import ensure_exists
from app.services.mappers import parse_tags, to_tag


class PublicPostService:

    def __init__(
        self,
        db: Session,
        post_repo: PostRepository | None = None,
        query_repo: PostDetailQueryRepository | None = None,
    ) -> None:
        self.db = db
        self.post_repo = post_repo or PostRepository(db)
        self.query_repo = query_repo or PostDetailQueryRepository(db)

    def get_posts(self, page: int, keyword: str | None) -> PostsPublishAtResponse:
        limit = Constant.PUBLIC_POST_LIMIT
        offset = (page - 1) * limit
        posts = self.post_repo.find_published_posts(offset, limit, keyword)

        total_count = self.post_repo.count_published_posts(keyword)
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0

        posts_list = []
        for post in posts:
            posts_list.append(
                PostPublishAt(
                    post_id=post.post_id,
                    title=post.title,
                    slug=post.slug,
                    thumbnail_url=post.thumbnail_url,
                    published_at=post.published_at,
                    tags=[to_tag(tag) for tag in post.tags],
                )
            )

        return PostsPublishAtResponse(
            total_count=total_count,
            total_pages=total_pages,
            page=page,
            limit=limit,
            posts=posts_list,
        )

    def get_slugs(self) -> PostSlugsResponse:
        slugs = self.post_repo.find_published_slugs()
        return PostSlugsResponse(slugs=slugs)

    def get_post(self, slug: str) -> PostPublishAtResponse:
        data = ensure_exists(self.query_repo.find_by_slug(slug))

        return PostPublishAtResponse(
            post_id=data.post_id,
            title=data.title,
            slug=data.slug,
            content_html=data.content_html,
            thumbnail_url=data.thumbnail_url,
            tags=parse_tags(data.tags),
            published_at=data.published_at,
        )
