import math
from sqlalchemy.orm import Session
from app.common.constant import Constant
from app.repositories.post_repository import PostRepository
from app.schemas.post import PostsPublishAtResponse, PostPublishAt


class PublicPostService:

    def __init__(self, db: Session):
        self.db = db
        self.post_repo = PostRepository(db)

    def get_posts(self, page: int, keyword: str | None) -> PostsPublishAtResponse:
        limit = Constant.PUBLIC_POST_LIMIT
        offset = (page - 1) * limit
        posts = self.post_repo.find_published_posts(offset, limit, keyword)

        total_count = len(posts)
        total_pages = math.ceil(total_count / limit)

        posts_list = []
        for post in posts:
            posts_list.append(
                PostPublishAt(
                    post_id=post.post_id,
                    title=post.title,
                    slug=post.slug,
                    thumbnail_url=post.thumbnail_url,
                    published_at=post.published_at,
                )
            )

        return PostsPublishAtResponse(
            total_count=total_count,
            total_pages=total_pages,
            page=page,
            limit=limit,
            posts=posts_list,
        )
