import math
from sqlalchemy.orm import Session
from app.common.constant import Constant
from app.repositories.post_repository import PostRepository
from app.repositories.queries.post_detail_query import PostDetailQueryRepository
from app.schemas.post import (
    PostsPublishAtResponse,
    PostPublishAt,
    PostPublishAtResponse,
)
from app.schemas.tag import Tag
from app.core.exceptions.handlers import ApplicationError
from app.common.message import ErrorMessage
from app.common.errorcode import ErrorCode


class PublicPostService:

    def __init__(self, db: Session):
        self.db = db
        self.post_repo = PostRepository(db)
        self.query_repo = PostDetailQueryRepository(db)

    def get_posts(self, page: int, keyword: str | None) -> PostsPublishAtResponse:
        limit = Constant.PUBLIC_POST_LIMIT
        offset = (page - 1) * limit
        posts = self.post_repo.find_published_posts(offset, limit, keyword)

        total_count = len(posts)
        total_pages = math.ceil(total_count / limit)

        posts_list = []
        for post in posts:
            tags = [
                Tag(
                    tag_id=tag.tag_id,
                    name=tag.name,
                    slug=tag.slug,
                )
                for tag in post.tags
            ]
            posts_list.append(
                PostPublishAt(
                    post_id=post.post_id,
                    title=post.title,
                    slug=post.slug,
                    thumbnail_url=post.thumbnail_url,
                    published_at=post.published_at,
                    tags=tags,
                )
            )

        return PostsPublishAtResponse(
            total_count=total_count,
            total_pages=total_pages,
            page=page,
            limit=limit,
            posts=posts_list,
        )

    def get_post(self, slug: str) -> PostPublishAtResponse:
        data = self.query_repo.find_by_slug(slug)
        tags = []

        if not data:
            raise ApplicationError(
                message=ErrorMessage.NOT_EXIST,
                code=ErrorCode.NOT_EXIST,
            )

        if data.tags:
            tags = [
                Tag(
                    tag_id=int(t[0]),
                    name=t[1],
                    slug=t[2],
                )
                for t in (tag.split("|") for tag in data.tags.split(","))
            ]

        return PostPublishAtResponse(
            post_id=data.post_id,
            title=data.title,
            slug=data.slug,
            content_html=data.content_html,
            thumbnail_url=data.thumbnail_url,
            tags=tags,
            published_at=data.published_at,
        )
