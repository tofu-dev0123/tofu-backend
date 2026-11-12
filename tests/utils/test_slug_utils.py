from unittest.mock import patch

from app.common.constant import Constant
from app.utils.slug_utils import (
    TRANSLATE_MAX_ATTEMPTS,
    generate_slug,
    is_draft_generated_slug,
    is_translation_failed,
    translate_to_english,
)

# 翻訳失敗時に Google が返すエラーページ本文
ERROR_PAGE_TEXT = (
    "Error 500 (Server Error)!!1500.That’s an error."
    "There was an error. Please try again later.That’s all we know."
)


# 翻訳結果の失敗判定: 正常な翻訳結果
def test_is_translation_failed_with_valid_text():
    assert is_translation_failed("I tried loop engineering") is False


# 翻訳結果の失敗判定: None・空文字
def test_is_translation_failed_with_empty_result():
    assert is_translation_failed(None) is True
    assert is_translation_failed("") is True
    assert is_translation_failed("   ") is True


# 翻訳結果の失敗判定: Googleのエラーページ本文
def test_is_translation_failed_with_error_page():
    assert is_translation_failed(ERROR_PAGE_TEXT) is True


# 翻訳成功→翻訳結果を返しリトライしない
@patch("app.utils.slug_utils.GoogleTranslator")
def test_translate_to_english_success(mock_translator):
    mock_translator.return_value.translate.return_value = "I tried loop engineering"

    result = translate_to_english("ループエンジニアリングを実践してみた")

    assert result == "I tried loop engineering"
    assert mock_translator.return_value.translate.call_count == 1


# 翻訳結果がNone→リトライ後にNoneを返す
@patch("app.utils.slug_utils.time.sleep")
@patch("app.utils.slug_utils.GoogleTranslator")
def test_translate_to_english_returns_none_when_result_is_none(
    mock_translator, mock_sleep
):
    mock_translator.return_value.translate.return_value = None

    result = translate_to_english("・")

    assert result is None
    assert mock_translator.return_value.translate.call_count == TRANSLATE_MAX_ATTEMPTS


# 翻訳結果がエラーページ本文→リトライ後にNoneを返す
@patch("app.utils.slug_utils.time.sleep")
@patch("app.utils.slug_utils.GoogleTranslator")
def test_translate_to_english_returns_none_when_error_page(mock_translator, mock_sleep):
    mock_translator.return_value.translate.return_value = ERROR_PAGE_TEXT

    result = translate_to_english("ループエンジニアリングを実践してみた")

    assert result is None
    assert mock_translator.return_value.translate.call_count == TRANSLATE_MAX_ATTEMPTS


# 翻訳が例外送出→リトライ後にNoneを返す
@patch("app.utils.slug_utils.time.sleep")
@patch("app.utils.slug_utils.GoogleTranslator")
def test_translate_to_english_returns_none_when_exception(mock_translator, mock_sleep):
    mock_translator.return_value.translate.side_effect = Exception("Error")

    result = translate_to_english("ループエンジニアリングを実践してみた")

    assert result is None
    assert mock_translator.return_value.translate.call_count == TRANSLATE_MAX_ATTEMPTS


# 1回目失敗・2回目成功→翻訳結果を返す
@patch("app.utils.slug_utils.time.sleep")
@patch("app.utils.slug_utils.GoogleTranslator")
def test_translate_to_english_success_after_retry(mock_translator, mock_sleep):
    mock_translator.return_value.translate.side_effect = [
        ERROR_PAGE_TEXT,
        "I tried loop engineering",
    ]

    result = translate_to_english("ループエンジニアリングを実践してみた")

    assert result == "I tried loop engineering"
    assert mock_translator.return_value.translate.call_count == 2
    assert mock_sleep.call_count == 1


# 翻訳成功→スラグを生成する
@patch("app.utils.slug_utils.translate_to_english", return_value="I tried loop engineering")
def test_generate_slug_success(mock_translate):
    assert generate_slug("ループエンジニアリングを実践してみた") == "i-tried-loop-engineering"


# 翻訳失敗→空文字を返す
@patch("app.utils.slug_utils.translate_to_english", return_value=None)
def test_generate_slug_returns_empty_when_translation_failed(mock_translate):
    assert generate_slug("・") == ""


# 最大文字数を超える→切り詰める
@patch("app.utils.slug_utils.translate_to_english")
def test_generate_slug_truncates_max_length(mock_translate):
    mock_translate.return_value = "a" * (Constant.MAX_SLUG_LENGTH + 10)

    result = generate_slug("長いタイトル")

    assert len(result) == Constant.MAX_SLUG_LENGTH


# ドラフトスラグの判定
def test_is_draft_generated_slug():
    assert is_draft_generated_slug("draft-0a1b2c3d") is True
    assert is_draft_generated_slug("i-tried-loop-engineering") is False
