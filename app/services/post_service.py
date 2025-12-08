import re
from deep_translator import GoogleTranslator
from slugify import slugify
from sqlalchemy.orm import Session
from app.core.mecab import tagger
from app.repositories.post_repository import find_slugs_like
from typing import List
from app.repositories.image_repository import find_by_image_id
from app.core.exceptions.post_exceptions import ImageNotExistError


"""
リクエストされた画像IDがImageテーブルに登録されているをチェックする
"""
def check_image_list(images: List[int], db: Session):
    for id in images:
        image_data = find_by_image_id(db, id)

        if image_data is None:
            raise ImageNotExistError(message="")
        

"""
翻訳を行う
"""
def translate_to_english(text: str) -> str:
    try:
        return GoogleTranslator(source="auto", target="en").translate(text)
    except Exception:
        return text  # 翻訳に失敗したら元の日本語でslugify


"""
リクエストされたタイトルからユニークなスラグを生成する
"""
def generate_unique_slug(title: str, db: Session) -> str:
    # 英語翻訳
    translated = translate_to_english(title)
    
    # ベーススラグ生成
    base_slug = slugify(translated)

    # DBから同一prefixのスラグ取得
    existing_slugs = find_slugs_like(db, base_slug)

    # 同じものがなければそのまま返す
    if base_slug not in existing_slugs:
        return base_slug

    # 末尾の数字を解析
    max_number = 0
    pattern = re.compile(rf"^{base_slug}-(\d+)$")

    for slug in existing_slugs:
        match = pattern.match(slug)
        if match:
            number = int(match.group(1))
            max_number = max(max_number, number)

    return f"{base_slug}-{max_number + 1}"
