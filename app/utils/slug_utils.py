import re
import unicodedata
import uuid
import pykakasi
from slugify import slugify
from app.common.constant import Constant

DRAFT_SLUG_PATTERN = re.compile(r"^draft-[0-9a-f]{8}$")

# 辞書の読み込みを毎回行わないようモジュールで 1 つだけ生成する
_kakasi = pykakasi.kakasi()


def generate_draft_slug() -> str:
    """タイトルなし下書き用の UUID ベーススラグを生成する"""
    return f"draft-{uuid.uuid4().hex[:8]}"


def is_draft_generated_slug(slug: str) -> bool:
    """自動生成された下書きスラグかどうかを判定する"""
    return bool(DRAFT_SLUG_PATTERN.match(slug))


def generate_fallback_tag_slug() -> str:
    """スラグを生成できなかったタグ用の UUID ベーススラグを生成する"""
    return f"tag-{uuid.uuid4().hex[:8]}"


"""
テキストをローマ字化する
"""


def to_romaji(text: str) -> str:
    # 全角英数を半角にそろえてからローマ字（ヘボン式）へ変換する
    normalized = unicodedata.normalize("NFKC", text)
    return " ".join(item["hepburn"] for item in _kakasi.convert(normalized))


"""
スラグを最大文字数以内に切り詰める
"""


def truncate_slug(slug: str) -> str:
    if len(slug) <= Constant.MAX_SLUG_LENGTH:
        return slug

    # 単語の途中で切らないよう、最大文字数 + 1 の範囲で最後のハイフン位置を探す
    hyphen_index = slug[: Constant.MAX_SLUG_LENGTH + 1].rfind("-")

    # ハイフンが無ければ文字数で切る
    if hyphen_index <= 0:
        return slug[: Constant.MAX_SLUG_LENGTH]

    return slug[:hyphen_index]


"""
テキストをローマ字化してスラグを生成する
"""


def generate_slug(text: str) -> str:
    # 生成結果が空の場合は空文字を返し、呼び出し元のフォールバックに委ねる
    return truncate_slug(slugify(to_romaji(text)))


"""
重複したスラグをインクリメントする
"""


def increment_slug_suffix(base_slug: str, existing_slugs: list[str]) -> str:
    # 末尾の数字を解析
    max_number = 0
    pattern = re.compile(rf"^{base_slug}-(\d+)$")

    for slug in existing_slugs:
        match = pattern.match(slug)
        if match:
            number = int(match.group(1))
            max_number = max(max_number, number)

    return f"{base_slug}-{max_number + 1}"
