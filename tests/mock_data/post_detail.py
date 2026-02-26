from datetime import datetime
from app.models.post import PostStatus


class DummyPostDetail:
    images: str | None
    tags: str | None

    def __init__(self):
        self.post_id = 1
        self.title = "テストタイトル"
        self.slug = "test-slug"
        self.content_md = "markdown"
        self.content_html = "<p>html</p>"
        self.thumbnail_url = "https://example.com/thumb.png"
        self.status = PostStatus.PUBLISHED
        self.images = (
            "1|https://example.com/img1.png|alt1,2|https://example.com/img2.png|alt2"
        )
        self.tags = "10|Python|python,20|FastAPI|fastapi"
        self.published_at = datetime(2025, 1, 1)
        self.created_at = datetime(2025, 1, 1)
        self.updated_at = datetime(2025, 1, 2)
