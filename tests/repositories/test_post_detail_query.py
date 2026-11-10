from datetime import datetime
from app.models.image import Image
from app.models.post import PostStatus
from app.models.post_tag import PostTag
from app.repositories.queries.post_detail_query import PostDetailQueryRepository


# 画像・タグを "id|...,id|..." 形式の集約文字列で返す
def test_find_by_post_id(db, make_post, make_tag):
    post = make_post("slug", title="title")
    python = make_tag("Python", "python")
    go = make_tag("Go", "go")
    db.add_all(
        [
            PostTag(post_id=post.post_id, tag_id=python.tag_id),
            PostTag(post_id=post.post_id, tag_id=go.tag_id),
            Image(post_id=post.post_id, url="https://cdn/a.png", alt_text="alt"),
            Image(post_id=post.post_id, url="https://cdn/b.png", alt_text=None),
        ]
    )
    db.flush()
    image_ids = [i.image_id for i in db.query(Image).order_by(Image.image_id)]

    row = PostDetailQueryRepository(db).find_by_post_id(post.post_id)

    assert row is not None
    assert row.post_id == post.post_id
    assert row.title == "title"
    assert row.status == PostStatus.DRAFT
    assert set(row.tags.split(",")) == {
        f"{python.tag_id}|Python|python",
        f"{go.tag_id}|Go|go",
    }
    # alt_text が NULL の場合は空文字になる
    assert set(row.images.split(",")) == {
        f"{image_ids[0]}|https://cdn/a.png|alt",
        f"{image_ids[1]}|https://cdn/b.png|",
    }


# 画像・タグがない場合は空文字（concat_ws が NULL を空文字にするため）、記事がない場合は行なし
def test_find_by_post_id_without_relations(db, make_post):
    post = make_post("slug")
    repo = PostDetailQueryRepository(db)

    row = repo.find_by_post_id(post.post_id)

    assert row is not None
    assert row.images == ""
    assert row.tags == ""
    assert repo.find_by_post_id(post.post_id + 1) is None


# 公開記事のみ slug で取得する
def test_find_by_slug(db, make_post, make_tag):
    post = make_post(
        "published", status=PostStatus.PUBLISHED, published_at=datetime(2024, 1, 1)
    )
    make_post("draft")
    tag = make_tag("Python", "python")
    db.add(PostTag(post_id=post.post_id, tag_id=tag.tag_id))
    db.flush()
    repo = PostDetailQueryRepository(db)

    row = repo.find_by_slug("published")

    assert row is not None
    assert row.post_id == post.post_id
    assert row.published_at == datetime(2024, 1, 1)
    assert row.tags == f"{tag.tag_id}|Python|python"
    assert repo.find_by_slug("draft") is None
    assert repo.find_by_slug("none") is None
