"""複数スキーマで共有するフィールドバリデータ

各スキーマでは `field_validator("<field>")(関数)` の形で割り当てる。
"""

from collections.abc import Callable
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


def max_length_validator(
    max_length: int, error_type: str
) -> Callable[[str | None], str | None]:
    """文字数が上限を超えたら error_type のエラーを送出するバリデータを返す

    同名フィールドでもスキーマごとに別メッセージを返したい場合に使う
    （メッセージは `(フィールド名, error_type)` で解決される）。
    """

    def validate(v: str | None) -> str | None:
        if v is not None and len(v) > max_length:
            raise PydanticCustomError(error_type, "")
        return v

    return validate
