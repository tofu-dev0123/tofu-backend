"""ORM モデル・集約文字列から Pydantic スキーマへの変換関数"""

from app.models.tag import Tag as TagModel
from app.models.product import Product as ProductModel
from app.models.timeline import Timeline as TimelineModel
from app.models.profile import Profile as ProfileModel
from app.schemas.tag import Tag
from app.schemas.image import Image
from app.schemas.product import Product
from app.schemas.timeline import Timeline
from app.schemas.profile import ProfileResponse

# 集約文字列の区切り（"id|name|slug,id|name|slug" 形式）
RECORD_SEPARATOR = ","
FIELD_SEPARATOR = "|"


def to_tag(tag: TagModel) -> Tag:
    return Tag(tag_id=tag.tag_id, name=tag.name, slug=tag.slug)


def to_product(product: ProductModel) -> Product:
    return Product(
        product_id=product.product_id,
        title=product.title,
        description=product.description,
        link_url=product.link_url,
        github_url=product.github_url,
        published=product.published,
        sort_order=product.sort_order,
        tags=[to_tag(tag) for tag in product.tags],
    )


def to_timeline(timeline: TimelineModel) -> Timeline:
    return Timeline(
        timeline_id=timeline.timeline_id,
        year=timeline.year,
        title=timeline.title,
        body=timeline.body,
        sort_order=timeline.sort_order,
    )


def to_profile(profile: ProfileModel) -> ProfileResponse:
    return ProfileResponse(
        headline=profile.headline,
        bio=profile.bio,
        site_description=profile.site_description,
    )


def _split_aggregated(aggregated: str | None) -> list[list[str]]:
    if not aggregated:
        return []
    return [
        record.split(FIELD_SEPARATOR)
        for record in aggregated.split(RECORD_SEPARATOR)
    ]


def parse_tags(aggregated: str | None) -> list[Tag]:
    """"tag_id|name|slug,..." 形式の集約文字列をタグ一覧に変換する"""
    return [
        Tag(tag_id=int(t[0]), name=t[1], slug=t[2])
        for t in _split_aggregated(aggregated)
    ]


def parse_images(aggregated: str | None) -> list[Image]:
    """"image_id|url|alt_text,..." 形式の集約文字列を画像一覧に変換する"""
    return [
        Image(image_id=int(i[0]), url=i[1], alt_text=i[2])
        for i in _split_aggregated(aggregated)
    ]
