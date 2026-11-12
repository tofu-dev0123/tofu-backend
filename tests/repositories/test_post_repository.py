from datetime import datetime
from app.models.post import Post, PostStatus
from app.models.post_tag import PostTag
from app.repositories.post_repository import PostRepository
from app.repositories.post_tag_repository import PostTagRepository


def test_create_and_find_by_post_id(db, test_user):
    repo = PostRepository(db)
    post = Post(
        user_id=test_user.user_id,
        title="title",
        slug="slug",
        content_md="md",
        content_html="<p>md</p>",
        status=PostStatus.DRAFT,
    )

    post_id = repo.create(post)

    assert repo.find_by_post_id(post_id) == post
    assert repo.exists_by_post_id(post_id) is True
    assert repo.exists_by_post_id(post_id + 1) is False
    assert repo.find_by_post_id(post_id + 1) is None


# 作成日時の降順、keyword / status で絞り込み、offset / limit で切り出す
def test_find_and_count_posts_by_user(db, test_user, make_post):
    repo = PostRepository(db)
    old = make_post("old", title="python old", created_at=datetime(2024, 1, 1))
    new = make_post(
        "new",
        title="python new",
        status=PostStatus.PUBLISHED,
        created_at=datetime(2024, 2, 1),
    )
    make_post("go", title="go", created_at=datetime(2024, 3, 1))

    assert [p.post_id for p in repo.find_posts_by_user(test_user.user_id, 0, 10, "python")] == [
        new.post_id,
        old.post_id,
    ]
    assert [
        p.post_id
        for p in repo.find_posts_by_user(test_user.user_id, 0, 10, None, PostStatus.PUBLISHED)
    ] == [new.post_id]
    assert len(repo.find_posts_by_user(test_user.user_id, 1, 1)) == 1
    assert repo.count_posts_by_user(test_user.user_id) == 3
    assert repo.count_posts_by_user(test_user.user_id, "python") == 2
    assert repo.count_posts_by_user(test_user.user_id, None, PostStatus.DRAFT) == 2


def test_get_post_counts(db, make_post):
    make_post("a", status=PostStatus.PUBLISHED, published_at=datetime(2024, 1, 1))
    make_post("b")
    make_post("c")

    counts = PostRepository(db).get_post_counts()

    assert counts.total_count == 3
    assert counts.published_count == 1
    assert counts.draft_count == 2


# 記事がない場合も 0 を返す
def test_get_post_counts_empty(db):
    counts = PostRepository(db).get_post_counts()

    assert (counts.total_count, counts.published_count, counts.draft_count) == (0, 0, 0)


def test_find_slugs_like(db, make_post):
    make_post("hello")
    make_post("hello-2")
    make_post("world")

    assert sorted(PostRepository(db).find_slugs_like("hello")) == ["hello", "hello-2"]


def test_find_thumbnail_url_by_post_id(db, make_post):
    post = make_post("a", thumbnail_url="https://cdn/thumb.png")
    repo = PostRepository(db)

    assert repo.find_thumbnail_url_by_post_id(post.post_id) == "https://cdn/thumb.png"
    assert repo.find_thumbnail_url_by_post_id(post.post_id + 1) is None


def test_update_post(db, make_post):
    post = make_post("old")
    repo = PostRepository(db)
    published_at = datetime(2024, 1, 1)

    repo.update_post(
        post_id=post.post_id,
        slug="new",
        title="new title",
        content_md="new md",
        content_html="<p>new</p>",
        status=PostStatus.PUBLISHED,
        published_at=published_at,
        thumbnail_url="https://cdn/t.png",
    )
    db.expire_all()

    updated = repo.find_by_post_id(post.post_id)
    assert updated is not None
    assert updated.slug == "new"
    assert updated.title == "new title"
    assert updated.content_md == "new md"
    assert updated.content_html == "<p>new</p>"
    assert updated.status == PostStatus.PUBLISHED
    assert updated.published_at == published_at
    assert updated.thumbnail_url == "https://cdn/t.png"


# slug 指定時のみ slug も更新する
def test_update_status_and_published_at(db, make_post):
    post = make_post("draft-slug")
    repo = PostRepository(db)
    published_at = datetime(2024, 1, 1)

    repo.update_status_and_published_at(post.post_id, PostStatus.PUBLISHED, published_at)
    db.expire_all()
    updated = repo.find_by_post_id(post.post_id)
    assert updated is not None
    assert updated.status == PostStatus.PUBLISHED
    assert updated.published_at == published_at
    assert updated.slug == "draft-slug"

    repo.update_status_and_published_at(
        post.post_id, PostStatus.PUBLISHED, published_at, slug="title-slug"
    )
    db.expire_all()
    updated = repo.find_by_post_id(post.post_id)
    assert updated is not None
    assert updated.slug == "title-slug"


# PostTagRepository で中間テーブルを削除してから記事を削除できる
def test_delete_with_post_tags(db, make_post, make_tag):
    post = make_post("a")
    tag = make_tag("Python", "python")
    post_tag_repo = PostTagRepository(db)
    post_tag_repo.create(PostTag(post_id=post.post_id, tag_id=tag.tag_id))
    db.flush()
    repo = PostRepository(db)

    post_tag_repo.delete_post_tags(post.post_id)
    repo.delete(post.post_id)

    assert repo.exists_by_post_id(post.post_id) is False
    assert db.query(PostTag).count() == 0


# 公開記事のみ、公開日時の降順、タグを読み込んで返す
def test_find_and_count_published_posts(db, make_post, make_tag):
    old = make_post(
        "old", title="python old", status=PostStatus.PUBLISHED, published_at=datetime(2024, 1, 1)
    )
    new = make_post(
        "new", title="python new", status=PostStatus.PUBLISHED, published_at=datetime(2024, 2, 1)
    )
    make_post("draft", title="python draft")
    tag = make_tag("Python", "python")
    PostTagRepository(db).create(PostTag(post_id=new.post_id, tag_id=tag.tag_id))
    db.flush()
    db.expire_all()
    repo = PostRepository(db)

    posts = repo.find_published_posts(0, 10)

    assert [p.post_id for p in posts] == [new.post_id, old.post_id]
    assert [t.slug for t in posts[0].tags] == ["python"]
    assert [p.post_id for p in repo.find_published_posts(0, 10, "new")] == [new.post_id]
    assert len(repo.find_published_posts(1, 1)) == 1
    assert repo.count_published_posts() == 2
    assert repo.count_published_posts("old") == 1
    assert sorted(repo.find_published_slugs()) == ["new", "old"]


def test_exists_by_slug(db, make_post):
    post = make_post("hello")
    repo = PostRepository(db)

    assert repo.exists_by_slug("hello") is True
    assert repo.exists_by_slug("world") is False
    # 自記事を除外すると重複なし
    assert repo.exists_by_slug("hello", exclude_post_id=post.post_id) is False
    assert repo.exists_by_slug("hello", exclude_post_id=post.post_id + 1) is True
