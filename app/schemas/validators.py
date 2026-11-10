"""複数スキーマで共有するフィールドバリデータ

各スキーマでは `field_validator("<field>")(関数)` の形で割り当てる。
"""

from pydantic_core import PydanticCustomError
from app.common.constant import Constant


def empty_string_to_none(v: str | None) -> str | None:
    """空文字列を None に変換する"""
    return None if v == "" else v


def validate_content_md_size(v: str) -> str:
    """Markdown 本文のバイトサイズ上限をチェックする"""
    if len(v.encode("utf-8")) > Constant.MAX_CONTENT_MARKDOWN_SIZE:
        raise PydanticCustomError("size_over", "")
    return v


def validate_tags(v: list[str]) -> list[str]:
    """タグの件数・文字数の上限をチェックする"""
    if len(v) > Constant.MAX_TAGS:
        raise PydanticCustomError("list_too_long", "")

    for tag in v:
        if len(tag) > Constant.MAX_TAG_LENGTH:
            raise PydanticCustomError("string_too_long", "")

    return v
