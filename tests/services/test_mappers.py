from unittest.mock import Mock
from app.services.mappers import (
    to_tag,
    to_product,
    to_timeline,
    to_profile,
    parse_tags,
    parse_images,
)
from app.schemas.tag import Tag
from app.schemas.image import Image


def _mock_tag(tag_id: int, name: str, slug: str) -> Mock:
    tag = Mock()
    tag.tag_id = tag_id
    tag.name = name
    tag.slug = slug
    return tag


# to_tag: タグモデルをスキーマに変換する
def test_to_tag():
    result = to_tag(_mock_tag(1, "Python", "python"))

    assert result == Tag(tag_id=1, name="Python", slug="python")


# to_product: タグを含めてプロダクトモデルをスキーマに変換する
def test_to_product():
    product = Mock()
    product.product_id = 1
    product.title = "title"
    product.description = None
    product.link_url = "https://example.com"
    product.github_url = None
    product.published = True
    product.sort_order = 2
    product.tags = [_mock_tag(10, "Python", "python"), _mock_tag(20, "Go", "go")]

    result = to_product(product)

    assert result.product_id == 1
    assert result.title == "title"
    assert result.description is None
    assert result.link_url == "https://example.com"
    assert result.github_url is None
    assert result.published is True
    assert result.sort_order == 2
    assert result.tags == [
        Tag(tag_id=10, name="Python", slug="python"),
        Tag(tag_id=20, name="Go", slug="go"),
    ]


# to_timeline: 年表モデルをスキーマに変換する
def test_to_timeline():
    timeline = Mock()
    timeline.timeline_id = 1
    timeline.year = 2024
    timeline.title = "title"
    timeline.body = None
    timeline.sort_order = 0

    result = to_timeline(timeline)

    assert result.timeline_id == 1
    assert result.year == 2024
    assert result.title == "title"
    assert result.body is None
    assert result.sort_order == 0


# to_profile: プロフィールモデルをスキーマに変換する
def test_to_profile():
    profile = Mock()
    profile.headline = "headline"
    profile.bio = "bio"
    profile.site_description = "desc"

    result = to_profile(profile)

    assert result.headline == "headline"
    assert result.bio == "bio"
    assert result.site_description == "desc"


# parse_tags: 集約文字列をタグ一覧に変換する
def test_parse_tags():
    result = parse_tags("1|Python|python,2|FastAPI|fastapi")

    assert result == [
        Tag(tag_id=1, name="Python", slug="python"),
        Tag(tag_id=2, name="FastAPI", slug="fastapi"),
    ]


# parse_tags: None / 空文字は空リストを返す
def test_parse_tags_empty():
    assert parse_tags(None) == []
    assert parse_tags("") == []


# parse_images: 集約文字列を画像一覧に変換する（代替テキストが空の場合も含む）
def test_parse_images():
    result = parse_images("1|https://example.com/a.png|alt,2|https://example.com/b.png|")

    assert result == [
        Image(image_id=1, url="https://example.com/a.png", alt_text="alt"),
        Image(image_id=2, url="https://example.com/b.png", alt_text=""),
    ]


# parse_images: None / 空文字は空リストを返す
def test_parse_images_empty():
    assert parse_images(None) == []
    assert parse_images("") == []
