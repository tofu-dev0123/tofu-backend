import logging
import re
import time
import uuid
from slugify import slugify
from sqlalchemy.orm import Session
from app.common.constant import Constant
from deep_translator import GoogleTranslator

logger = logging.getLogger(__name__)

DRAFT_SLUG_PATTERN = re.compile(r"^draft-[0-9a-f]{8}$")

# 翻訳に失敗した際に Google が 200 で返すエラーページ本文のパターン
TRANSLATION_ERROR_PATTERNS = (
    re.compile(r"Error\s+\d+\s+\(.*Error\)", re.IGNORECASE),
    re.compile(r"That.s an error", re.IGNORECASE),
)

# 翻訳の試行回数と初回リトライ待機秒数（指数バックオフ）
TRANSLATE_MAX_ATTEMPTS = 3
TRANSLATE_RETRY_WAIT_SECONDS = 0.5


def generate_draft_slug() -> str:
    """タイトルなし下書き用の UUID ベーススラグを生成する"""
    return f"draft-{uuid.uuid4().hex[:8]}"


def is_draft_generated_slug(slug: str) -> bool:
    """自動生成された下書きスラグかどうかを判定する"""
    return bool(DRAFT_SLUG_PATTERN.match(slug))


def generate_fallback_tag_slug() -> str:
    """スラグを生成できなかったタグ用の UUID ベーススラグを生成する"""
    return f"tag-{uuid.uuid4().hex[:8]}"


def is_translation_failed(translated: str | None) -> bool:
    """翻訳結果が失敗を示すものかどうかを判定する"""
    if translated is None or not translated.strip():
        return True

    return any(pattern.search(translated) for pattern in TRANSLATION_ERROR_PATTERNS)


"""
翻訳を行う
"""


def translate_to_english(text: str) -> str | None:
    """英語へ翻訳する。失敗した場合は None を返す"""
    for attempt in range(TRANSLATE_MAX_ATTEMPTS):
        try:
            translated = GoogleTranslator(source="auto", target="en").translate(text)
        except Exception:
            translated = None

        if not is_translation_failed(translated):
            return translated

        # 最終試行でなければ指数バックオフで待機してリトライする
        if attempt < TRANSLATE_MAX_ATTEMPTS - 1:
            time.sleep(TRANSLATE_RETRY_WAIT_SECONDS * (2**attempt))

    logger.warning("translation failed", extra={"attempts": TRANSLATE_MAX_ATTEMPTS})

    return None


"""
テキストを翻訳してスラグを生成する
"""


def generate_slug(text: str) -> str:
    # 英語翻訳（失敗時は空文字を返し、呼び出し元のフォールバックに委ねる）
    translated = translate_to_english(text)

    if translated is None:
        return ""

    # ベーススラグ生成
    slug = slugify(translated)

    # スラグが最大文字数を超えた場合は切り取る
    if len(slug) > Constant.MAX_SLUG_LENGTH:
        slug = slug[: Constant.MAX_SLUG_LENGTH]

    return slug


"""
重複したスラグをインクリメントする
"""


def increment_slug_suffix(base_slug: str, existing_slugs: list[str]):
    # 末尾の数字を解析
    max_number = 0
    pattern = re.compile(rf"^{base_slug}-(\d+)$")

    for slug in existing_slugs:
        match = pattern.match(slug)
        if match:
            number = int(match.group(1))
            max_number = max(max_number, number)

    return f"{base_slug}-{max_number + 1}"
