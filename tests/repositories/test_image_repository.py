from app.models.image import Image
from app.repositories.image_repository import ImageRepository


def test_create_and_find(db):
    repo = ImageRepository(db)

    image_id = repo.create(Image(url="https://cdn/a.png", alt_text="alt"))

    image = repo.find_by_image_id(image_id)
    assert image is not None
    assert image.url == "https://cdn/a.png"
    assert repo.find_by_url("https://cdn/a.png") == image
    assert repo.find_by_image_id(image_id + 1) is None
    assert repo.find_by_url("https://cdn/none.png") is None


def test_update_post_id_and_find_url_by_post_id(db, make_post):
    repo = ImageRepository(db)
    post = make_post("slug")
    a = repo.create(Image(url="https://cdn/a.png"))
    repo.create(Image(url="https://cdn/b.png"))

    repo.update_post_id(a, post.post_id)

    assert repo.find_url_by_post_id(post.post_id) == ["https://cdn/a.png"]


def test_delete(db):
    repo = ImageRepository(db)
    image_id = repo.create(Image(url="https://cdn/a.png"))

    repo.delete(image_id)

    assert repo.find_by_image_id(image_id) is None


def test_delete_from_post_id(db, make_post):
    repo = ImageRepository(db)
    post = make_post("slug")
    repo.create(Image(url="https://cdn/a.png", post_id=post.post_id))
    other = repo.create(Image(url="https://cdn/b.png"))

    repo.delete_from_post_id(post.post_id)

    assert repo.find_url_by_post_id(post.post_id) == []
    assert repo.find_by_image_id(other) is not None
