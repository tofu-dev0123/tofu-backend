import pytest

from app.common.constant import Constant
from app.utils.slug_utils import (
    generate_slug,
    is_draft_generated_slug,
    truncate_slug,
)


# 日本語・英語混じりのタイトル→ローマ字スラグを生成する
@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("ループエンジニアリングを実践してみた", "ruupuenjiniaringu-wo-jissen-shitemita"),
        ("【検索処理】転置インデックスについて", "kensakushori-tenchi-indekkusu-nitsuite"),
        ("Docker入門", "docker-nyuumon"),
        ("FastAPI", "fastapi"),
    ],
)
def test_generate_slug_success(text, expected):
    assert generate_slug(text) == expected


# 記号のみ→空文字を返す
def test_generate_slug_returns_empty_when_only_symbols():
    assert generate_slug("・！？") == ""


# 全角英数→半角に正規化してスラグを生成する
def test_generate_slug_normalizes_full_width():
    assert generate_slug("ＡＢＣ１２３") == "abc123"


# 最大文字数を超える→単語の途中で切らずに切り詰める
def test_generate_slug_truncates_at_hyphen_boundary():
    result = generate_slug(
        "【Shelfie】DevLog #05 | Clerk から独自 OAuth プロバイダへ移行した話"
    )

    assert result == "shelfie-devlog-05-clerk-kara-dokuji-oauth"
    assert len(result) <= Constant.MAX_SLUG_LENGTH


# 最大文字数ちょうどの位置がハイフン→その手前までを返す
def test_truncate_slug_when_hyphen_at_boundary():
    word = "a" * Constant.MAX_SLUG_LENGTH

    assert truncate_slug(f"{word}-b") == word


# ハイフンが無い長い文字列→文字数で切り詰める
def test_truncate_slug_without_hyphen():
    result = truncate_slug("a" * (Constant.MAX_SLUG_LENGTH + 10))

    assert result == "a" * Constant.MAX_SLUG_LENGTH


# 最大文字数以内→そのまま返す
def test_truncate_slug_within_max_length():
    assert truncate_slug("docker-nyuumon") == "docker-nyuumon"


# ドラフトスラグの判定
def test_is_draft_generated_slug():
    assert is_draft_generated_slug("draft-0a1b2c3d") is True
    assert is_draft_generated_slug("i-tried-loop-engineering") is False
