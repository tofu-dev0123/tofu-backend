import re
from slugify import slugify
from sqlalchemy.orm import Session
from typing import List
from app.common.constant import Constant
from deep_translator import GoogleTranslator

"""
翻訳を行う
"""


def translate_to_english(text: str) -> str:
    try:
        return GoogleTranslator(source="auto", target="en").translate(text)
    except Exception:
        return text  # 翻訳に失敗したら元の日本語でslugify


"""
テキストを翻訳してスラグを生成する
"""


def generate_slug(text: str) -> str:
    # 英語翻訳
    translated = translate_to_english(text)

    # ベーススラグ生成
    slug = slugify(translated)

    # スラグが最大文字数を超えた場合は切り取る
    if len(slug) > Constant.MAX_SLUG_LENGTH:
        slug = slug[: Constant.MAX_SLUG_LENGTH]

    return slug


"""
重複したスラグをインクリメントする
"""


def increment_slug_suffix(base_slug: str, existing_slugs: List[str]):
    # 末尾の数字を解析
    max_number = 0
    pattern = re.compile(rf"^{base_slug}-(\d+)$")

    for slug in existing_slugs:
        match = pattern.match(slug)
        if match:
            number = int(match.group(1))
            max_number = max(max_number, number)

    return f"{base_slug}-{max_number + 1}"
